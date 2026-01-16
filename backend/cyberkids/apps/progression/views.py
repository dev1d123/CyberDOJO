from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import ProgressionLevel, CosmeticItem, UserInventory, CreditTransaction, UserProgress
from .serializers import (
    ProgressionLevelSerializer, CosmeticItemSerializer,
    UserInventorySerializer, CreditTransactionSerializer, UserProgressSerializer
)
from apps.cyberUser.models import CyberUser
from apps.pets.models import Pet, UserPet
from apps.pets.serializers import PetSerializer, UserPetSerializer


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

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_transactions(self, request):
        """Lista las transacciones del usuario autenticado."""
        transactions = CreditTransaction.objects.filter(user=request.user).order_by('-created_at')[:50]
        return Response(CreditTransactionSerializer(transactions, many=True).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_balance(self, request):
        """Muestra el balance y resumen de transacciones del usuario."""
        user = request.user
        transactions = CreditTransaction.objects.filter(user=user)
        
        total_earned = sum(t.amount for t in transactions if t.amount > 0)
        total_spent = abs(sum(t.amount for t in transactions if t.amount < 0))
        
        return Response({
            'current_balance': user.cybercreds,
            'total_earned': total_earned,
            'total_spent': total_spent,
            'transaction_count': transactions.count()
        })


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

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_progress(self, request):
        """Obtener progreso del usuario autenticado."""
        progress = UserProgress.objects.filter(user=request.user).select_related('current_level').first()
        
        if not progress:
            # Crear progreso inicial si no existe
            first_level = ProgressionLevel.objects.filter(level_number=1).first()
            progress = UserProgress.objects.create(
                user=request.user,
                current_level=first_level,
                current_xp=0
            )
        
        # Calcular XP necesario para siguiente nivel
        next_level = ProgressionLevel.objects.filter(
            level_number__gt=progress.current_level.level_number if progress.current_level else 0
        ).order_by('level_number').first()
        
        xp_for_next = next_level.required_xp if next_level else None
        xp_progress = progress.current_xp - (progress.current_level.required_xp if progress.current_level else 0)
        xp_needed = (next_level.required_xp - progress.current_level.required_xp) if next_level and progress.current_level else 0
        
        return Response({
            'progress': UserProgressSerializer(progress).data,
            'next_level': next_level.level_number if next_level else None,
            'xp_for_next_level': xp_for_next,
            'xp_progress_to_next': xp_progress,
            'xp_needed_for_next': xp_needed,
            'percentage_to_next': round((xp_progress / xp_needed * 100) if xp_needed > 0 else 100, 1)
        })

    @action(detail=False, methods=['get'])
    def leaderboard(self, request):
        """Top 20 usuarios por nivel y XP."""
        top_users = UserProgress.objects.select_related('user', 'current_level').order_by(
            '-current_level__level_number', '-current_xp'
        )[:20]
        
        result = []
        for i, progress in enumerate(top_users, 1):
            result.append({
                'rank': i,
                'username': progress.user.username,
                'level': progress.current_level.level_number if progress.current_level else 1,
                'level_name': progress.current_level.name if progress.current_level else 'Principiante',
                'xp': progress.current_xp,
                'games_won': progress.games_won,
            })
        
        return Response(result)

    @action(detail=False, methods=['get'])
    def leaderboard_cybercreds(self, request):
        """Top 20 usuarios por cybercreds."""
        top_users = CyberUser.objects.filter(is_active=True).order_by('-cybercreds')[:20]
        
        result = []
        for i, user in enumerate(top_users, 1):
            result.append({
                'rank': i,
                'username': user.username,
                'cybercreds': user.cybercreds,
            })
        
        return Response(result)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_rank(self, request):
        """Obtener el ranking del usuario autenticado."""
        user = request.user
        progress = UserProgress.objects.filter(user=user).first()
        
        if not progress:
            return Response({
                'rank': None,
                'message': 'Sin progreso registrado'
            })
        
        # Contar usuarios con mejor nivel/XP
        better_users = UserProgress.objects.filter(
            current_level__level_number__gt=progress.current_level.level_number if progress.current_level else 0
        ).count()
        
        same_level_better_xp = UserProgress.objects.filter(
            current_level=progress.current_level,
            current_xp__gt=progress.current_xp
        ).count()
        
        rank = better_users + same_level_better_xp + 1
        total_users = UserProgress.objects.count()
        
        return Response({
            'rank': rank,
            'total_users': total_users,
            'percentile': round((1 - rank / total_users) * 100, 1) if total_users > 0 else 0
        })

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def get_user_progress(self, request, user_id=None):
        """Obtener progreso de un usuario."""
        progress = UserProgress.objects.filter(user_id=user_id).first()
        if progress:
            return Response(UserProgressSerializer(progress).data)
        return Response({'error': 'Sin progreso registrado'}, status=status.HTTP_404_NOT_FOUND)


class ShopViewSet(viewsets.ViewSet):
    """
    ViewSet unificado para la tienda.
    Permite comprar mascotas (pets) e items cosméticos.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def all(self, request):
        """Lista todos los items disponibles en la tienda (pets y cosméticos)."""
        pets = Pet.objects.filter(is_default=False)
        cosmetics = CosmeticItem.objects.filter(is_active=True)
        
        return Response({
            'pets': PetSerializer(pets, many=True).data,
            'cosmetics': CosmeticItemSerializer(cosmetics, many=True).data
        })

    @action(detail=False, methods=['get'])
    def pets(self, request):
        """Lista mascotas disponibles para comprar."""
        pets = Pet.objects.filter(is_default=False)
        return Response(PetSerializer(pets, many=True).data)

    @action(detail=False, methods=['get'])
    def cosmetics(self, request):
        """Lista items cosméticos disponibles para comprar."""
        items = CosmeticItem.objects.filter(is_active=True)
        return Response(CosmeticItemSerializer(items, many=True).data)

    @action(detail=False, methods=['post'], url_path='buy-pet')
    def buy_pet(self, request):
        """Comprar una mascota con cybercreds."""
        user = request.user  # Ya es CyberUser gracias a JWTCustomAuthentication
        pet_id = request.data.get('pet_id')

        if not pet_id:
            return Response({'error': 'pet_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        pet = get_object_or_404(Pet, pk=pet_id)

        # Verificar si ya tiene la mascota
        if UserPet.objects.filter(user=user, pet=pet).exists():
            return Response({'error': 'Ya tienes esta mascota'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar cybercreds
        if user.cybercreds < pet.cybercreds_cost:
            return Response({'error': 'No tienes suficientes cybercreds'}, status=status.HTTP_400_BAD_REQUEST)

        # Descontar cybercreds
        user.cybercreds -= pet.cybercreds_cost
        user.save(update_fields=['cybercreds'])

        # Registrar transacción
        CreditTransaction.objects.create(
            user=user,
            amount=-pet.cybercreds_cost,
            transaction_type='purchase',
            description=f'Compra de mascota: {pet.name}',
            reference_id=pet.pet_id,
            reference_type='pet'
        )

        # Crear relación usuario-mascota
        user_pet = UserPet.objects.create(user=user, pet=pet)

        return Response({
            'message': f'Has comprado a {pet.name}!',
            'user_pet': UserPetSerializer(user_pet).data,
            'remaining_cybercreds': user.cybercreds
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='buy-cosmetic')
    def buy_cosmetic(self, request):
        """Comprar un item cosmético con cybercreds."""
        user = request.user  # Ya es CyberUser gracias a JWTCustomAuthentication
        item_id = request.data.get('item_id')

        if not item_id:
            return Response({'error': 'item_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(CosmeticItem, pk=item_id)

        # Verificar si ya tiene el item
        if UserInventory.objects.filter(user=user, item=item).exists():
            return Response({'error': 'Ya tienes este item'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar nivel requerido
        progress = UserProgress.objects.filter(user=user).first()
        if item.required_level > 1:
            if not progress or not progress.current_level:
                return Response({'error': f'Necesitas nivel {item.required_level}'}, status=status.HTTP_400_BAD_REQUEST)
            if progress.current_level.level_number < item.required_level:
                return Response({'error': f'Necesitas nivel {item.required_level}'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar cybercreds
        if user.cybercreds < item.cybercreds_cost:
            return Response({'error': 'No tienes suficientes cybercreds'}, status=status.HTTP_400_BAD_REQUEST)

        # Descontar cybercreds
        user.cybercreds -= item.cybercreds_cost
        user.save(update_fields=['cybercreds'])

        # Registrar transacción
        CreditTransaction.objects.create(
            user=user,
            amount=-item.cybercreds_cost,
            transaction_type='purchase',
            description=f'Compra de cosmético: {item.name}',
            reference_id=item.item_id,
            reference_type='cosmetic_item'
        )

        # Crear inventario
        inventory = UserInventory.objects.create(user=user, item=item)

        return Response({
            'message': f'Has comprado {item.name}!',
            'inventory': UserInventorySerializer(inventory).data,
            'remaining_cybercreds': user.cybercreds
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='my-purchases')
    def my_purchases(self, request):
        """Obtiene todas las compras del usuario autenticado."""
        user = request.user
        
        user_pets = UserPet.objects.filter(user=user).select_related('pet')
        user_inventory = UserInventory.objects.filter(user=user).select_related('item')
        
        return Response({
            'pets': UserPetSerializer(user_pets, many=True).data,
            'cosmetics': UserInventorySerializer(user_inventory, many=True).data,
            'cybercreds': user.cybercreds
        })

    @action(detail=False, methods=['post'], url_path='equip-pet')
    def equip_pet(self, request):
        """Equipar una mascota."""
        user = request.user
        pet_id = request.data.get('pet_id')

        if not pet_id:
            return Response({'error': 'pet_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar que el usuario tiene la mascota
        user_pet = UserPet.objects.filter(user=user, pet_id=pet_id).first()
        if not user_pet:
            return Response({'error': 'No tienes esta mascota'}, status=status.HTTP_404_NOT_FOUND)

        # Desequipar todas las mascotas del usuario
        UserPet.objects.filter(user=user).update(is_equipped=False)

        # Equipar la seleccionada
        user_pet.is_equipped = True
        user_pet.save(update_fields=['is_equipped'])

        # Actualizar pet_id en usuario
        user.pet_id = pet_id
        user.save(update_fields=['pet_id'])

        return Response({
            'message': f'Has equipado a {user_pet.pet.name}!',
            'user_pet': UserPetSerializer(user_pet).data
        })

    @action(detail=False, methods=['post'], url_path='equip-cosmetic')
    def equip_cosmetic(self, request):
        """Equipar un item cosmético."""
        user = request.user
        item_id = request.data.get('item_id')

        if not item_id:
            return Response({'error': 'item_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(CosmeticItem, pk=item_id)

        # Verificar que el usuario tiene el item
        inventory = UserInventory.objects.filter(user=user, item=item).first()
        if not inventory:
            return Response({'error': 'No tienes este item'}, status=status.HTTP_404_NOT_FOUND)

        # Desequipar items del mismo tipo
        UserInventory.objects.filter(user=user, item__type=item.type).update(is_equipped=False)

        # Equipar el seleccionado
        inventory.is_equipped = True
        inventory.save(update_fields=['is_equipped'])

        return Response({
            'message': f'Has equipado {item.name}!',
            'inventory': UserInventorySerializer(inventory).data
        })
