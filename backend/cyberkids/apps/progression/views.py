from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import ProgressionLevel, CosmeticItem, UserInventory, CreditTransaction, UserProgress
from .serializers import (
    ProgressionLevelSerializer, CosmeticItemSerializer,
    UserInventorySerializer, CreditTransactionSerializer, UserProgressSerializer
)
from apps.cyberUser.models import CyberUser


class ProgressionLevelViewSet(viewsets.ModelViewSet):
    queryset = ProgressionLevel.objects.all().order_by('level_number')
    serializer_class = ProgressionLevelSerializer


class CosmeticItemViewSet(viewsets.ModelViewSet):
    queryset = CosmeticItem.objects.all()
    serializer_class = CosmeticItemSerializer

    def get_queryset(self):
        queryset = CosmeticItem.objects.filter(is_active=True)
        item_type = self.request.query_params.get('type')
        if item_type:
            queryset = queryset.filter(type=item_type)
        return queryset

    @action(detail=False, methods=['get'])
    def shop(self, request):
        """Lista items disponibles en la tienda."""
        items = CosmeticItem.objects.filter(is_active=True)
        return Response(CosmeticItemSerializer(items, many=True).data)


class UserInventoryViewSet(viewsets.ModelViewSet):
    queryset = UserInventory.objects.all()
    serializer_class = UserInventorySerializer

    def get_queryset(self):
        queryset = UserInventory.objects.select_related('item')
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    @action(detail=False, methods=['post'])
    def buy(self, request):
        """Comprar un item cosmético."""
        user_id = request.data.get('user_id')
        item_id = request.data.get('item_id')

        user = get_object_or_404(CyberUser, pk=user_id)
        item = get_object_or_404(CosmeticItem, pk=item_id)

        # Verificar si ya tiene el item
        if UserInventory.objects.filter(user=user, item=item).exists():
            return Response({'error': 'Ya tienes este item'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar nivel requerido
        progress = UserProgress.objects.filter(user=user).first()
        if progress and progress.current_level:
            if progress.current_level.level_number < item.required_level:
                return Response({'error': f'Necesitas nivel {item.required_level}'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar cybercreds
        if user.cybercreds < item.cybercreds_cost:
            return Response({'error': 'No tienes suficientes cybercreds'}, status=status.HTTP_400_BAD_REQUEST)

        # Descontar y crear
        user.cybercreds -= item.cybercreds_cost
        user.save(update_fields=['cybercreds'])

        # Registrar transacción
        CreditTransaction.objects.create(
            user=user,
            amount=-item.cybercreds_cost,
            transaction_type='purchase',
            description=f'Compra: {item.name}',
            reference_id=item.item_id,
            reference_type='cosmetic_item'
        )

        inventory = UserInventory.objects.create(user=user, item=item)
        return Response(UserInventorySerializer(inventory).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def equip(self, request):
        """Equipar un item cosmético."""
        user_id = request.data.get('user_id')
        item_id = request.data.get('item_id')

        user = get_object_or_404(CyberUser, pk=user_id)
        item = get_object_or_404(CosmeticItem, pk=item_id)

        # Desequipar items del mismo tipo
        UserInventory.objects.filter(user=user, item__type=item.type).update(is_equipped=False)

        # Equipar el seleccionado
        inventory = get_object_or_404(UserInventory, user=user, item=item)
        inventory.is_equipped = True
        inventory.save(update_fields=['is_equipped'])

        return Response(UserInventorySerializer(inventory).data)


class CreditTransactionViewSet(viewsets.ModelViewSet):
    queryset = CreditTransaction.objects.all()
    serializer_class = CreditTransactionSerializer

    def get_queryset(self):
        queryset = CreditTransaction.objects.all().order_by('-created_at')
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset


class UserProgressViewSet(viewsets.ModelViewSet):
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer

    def get_queryset(self):
        queryset = UserProgress.objects.select_related('current_level')
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    @action(detail=False, methods=['post'])
    def add_xp(self, request):
        """Añadir XP y verificar subida de nivel."""
        user_id = request.data.get('user_id')
        xp_amount = request.data.get('xp', 0)

        user = get_object_or_404(CyberUser, pk=user_id)
        progress, created = UserProgress.objects.get_or_create(
            user=user,
            defaults={'current_xp': 0, 'current_level': ProgressionLevel.objects.filter(level_number=1).first()}
        )

        progress.current_xp += xp_amount
        leveled_up = False

        # Verificar subida de nivel
        next_level = ProgressionLevel.objects.filter(
            level_number__gt=progress.current_level.level_number if progress.current_level else 0,
            required_xp__lte=progress.current_xp
        ).order_by('-level_number').first()

        if next_level and (not progress.current_level or next_level.level_number > progress.current_level.level_number):
            progress.current_level = next_level
            leveled_up = True
            
            # Dar recompensa de cybercreds
            if next_level.cybercreds_reward > 0:
                user.cybercreds += next_level.cybercreds_reward
                user.save(update_fields=['cybercreds'])
                
                CreditTransaction.objects.create(
                    user=user,
                    amount=next_level.cybercreds_reward,
                    transaction_type='bonus',
                    description=f'Subida a nivel {next_level.level_number}',
                    reference_id=next_level.level_id,
                    reference_type='progression_level'
                )

        progress.save()

        return Response({
            'progress': UserProgressSerializer(progress).data,
            'leveled_up': leveled_up,
            'new_level': next_level.level_number if leveled_up else None
        })

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def get_user_progress(self, request, user_id=None):
        """Obtener progreso de un usuario."""
        progress = UserProgress.objects.filter(user_id=user_id).first()
        if progress:
            return Response(UserProgressSerializer(progress).data)
        return Response({'error': 'Sin progreso registrado'}, status=status.HTTP_404_NOT_FOUND)
