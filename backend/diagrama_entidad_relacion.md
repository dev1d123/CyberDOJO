# Entity-Relationship Diagram - CyberKids Security Platform

## System Description
Gamified web platform to teach at-risk children to recognize social engineering threats.

---

## ER Diagram for dbdiagram.io

Copy and paste the following code at [https://dbdiagram.io](https://dbdiagram.io):

```dbml
// ==========================================
// CYBERKIDS SECURITY PLATFORM - DATABASE SCHEMA
// ==========================================

// ==========================================
// MAIN USER ENTITIES
// ==========================================

Table user {
  user_id int [pk, increment]
  username varchar(50) [not null]
  email varchar(100) [unique, not null]
  password_hash varchar(255) [not null]
  country_id int [ref: > country.country_id]
  risk_level_id int [ref: > risk_level.risk_level_id]
  pet_id int [ref: > pet.pet_id, note: 'Currently equipped pet']
  cybercreds int [default: 0]
  created_at datetime [default: `now()`]
  last_login datetime
  is_active boolean [default: true]
}

Table country {
  country_id int [pk, increment]
  name varchar(100) [not null]
  iso_code varchar(3) [unique, not null]
  language varchar(50)
  is_active boolean [default: true]
}

Table risk_level {
  risk_level_id int [pk, increment]
  name varchar(20) [not null, note: 'Low, Medium, High']
  description varchar(255)
  ai_difficulty int [note: 'AI aggressiveness level']
  points_multiplier float [default: 1.0]
}

// ==========================================
// RF-01: CULTURAL PERSONALIZATION (SLANG ENGINE)
// ==========================================

Table slang {
  slang_id int [pk, increment]
  country_id int [ref: > country.country_id, not null]
  formal_term varchar(100) [not null]
  local_term varchar(100) [not null, note: 'E.g.: buddy, mate, dude']
  usage_context varchar(255)
  category varchar(50) [note: 'noun, verb, expression']
  is_active boolean [default: true]

  indexes {
    (country_id, formal_term) [unique]
  }
}

Table system_prompt_template {
  template_id int [pk, increment]
  country_id int [ref: > country.country_id, not null]
  base_content text [not null]
  tone_instructions     
  version varchar(20)
  is_active boolean [default: true]
}

// ==========================================
// RF-02: SOCIAL ENGINEERING SIMULATION
// ==========================================

Table scenario {
  scenario_id int [pk, increment]
  name varchar(100) [not null]
  description text
  antagonist_goal varchar(100) [not null, note: 'password, photos, meetup, location']
  difficulty_level int [not null, note: '1-5']
  base_points int [default: 100]
  threat_type varchar(50) [note: 'phishing, grooming, sextortion']
  is_active boolean [default: true]
}

Table sensitive_pattern {
  pattern_id int [pk, increment]
  name varchar(100) [not null]
  regex_pattern varchar(500) [not null]
  data_type varchar(50) [not null, note: 'SSN, Phone, Email, Address']
  alert_message varchar(255)
  severity int [default: 1, note: '1-5']
}

Table game_session {
  session_id int [pk, increment]
  user_id int [ref: > user.user_id, not null]
  scenario_id int [ref: > scenario.scenario_id, not null]
  started_at datetime [default: `now()`]
  ended_at datetime
  status varchar(20) [default: 'in_progress', note: 'in_progress, completed, game_over']
  points_earned int [default: 0]
  is_game_over boolean [default: false]
  game_over_reason varchar(255)

  indexes {
    user_id
    started_at
  }
}

Table chat_message {
  message_id int [pk, increment]
  session_id int [ref: > game_session.session_id, not null]
  role varchar(20) [not null, note: 'user, antagonist, system']
  content text [not null]
  sent_at datetime [default: `now()`]
  is_dangerous boolean [default: false]
  detected_pattern_id int [ref: > sensitive_pattern.pattern_id]

  indexes {
    session_id
  }
}

// ==========================================
// RF-03: EMOTIONAL FEEDBACK SYSTEM (PET)
// ==========================================

Table pet {
  pet_id int [pk, increment]
  name varchar(50) [not null]
  description varchar(255)
  base_sprite_url varchar(255)
  cybercreds_cost int [default: 0]
  is_default boolean [default: false]
}

Table pet_state {
  state_id int [pk, increment]
  pet_id int [ref: > pet.pet_id, not null]
  state_name varchar(50) [not null, note: 'Error, Success, Thinking, Idle']
  svg_url varchar(255)
  animation_url varchar(255)
  duration_ms int [default: 500, note: 'RF-03: must be < 500ms']
}

Table user_pet {
  user_pet_id int [pk, increment]
  user_id int [ref: > user.user_id, not null]
  pet_id int [ref: > pet.pet_id, not null]
  is_equipped boolean [default: false]
  acquired_at datetime [default: `now()`]

  indexes {
    (user_id, pet_id) [unique]
  }
}

// ==========================================
// RF-04: GAMIFIED EVENTS (MINIGAMES)
// ==========================================

Table minigame {
  minigame_id int [pk, increment]
  name varchar(100) [not null]
  type varchar(50) [not null, note: 'swipe, quiz, memory']
  description text
  base_points int [default: 50]
  time_limit_sec int
  is_active boolean [default: true]
}

Table swipe_question {
  question_id int [pk, increment]
  minigame_id int [ref: > minigame.minigame_id, not null]
  notification_content text [not null]
  correct_answer varchar(20) [not null, note: 'Safe, Dangerous']
  explanation text
  difficulty_level int [default: 1]
  country_id int [ref: > country.country_id, note: 'For localization']
}

Table minigame_session {
  minigame_session_id int [pk, increment]
  user_id int [ref: > user.user_id, not null]
  minigame_id int [ref: > minigame.minigame_id, not null]
  played_at datetime [default: `now()`]
  points_earned int [default: 0]
  correct_answers int [default: 0]
  incorrect_answers int [default: 0]
  time_spent_sec int

  indexes {
    user_id
  }
}

Table swipe_response {
  response_id int [pk, increment]
  minigame_session_id int [ref: > minigame_session.minigame_session_id, not null]
  question_id int [ref: > swipe_question.question_id, not null]
  user_answer varchar(20) [not null]
  is_correct boolean
  response_time_ms int
}

// ==========================================
// RF-05: PROGRESSION AND ECONOMY
// ==========================================

Table progression_level {
  level_id int [pk, increment]
  level_number int [unique, not null]
  name varchar(50)
  required_xp int [not null]
  cybercreds_reward int [default: 0]
  badge_url varchar(255)
}

Table cosmetic_item {
  item_id int [pk, increment]
  name varchar(100) [not null]
  type varchar(50) [not null, note: 'avatar, frame, background, effect']
  description varchar(255)
  preview_url varchar(255)
  cybercreds_cost int [not null]
  required_level int [default: 1]
  is_active boolean [default: true]
}

Table user_inventory {
  inventory_id int [pk, increment]
  user_id int [ref: > user.user_id, not null]
  item_id int [ref: > cosmetic_item.item_id, not null]
  acquired_at datetime [default: `now()`]
  is_equipped boolean [default: false]

  indexes {
    (user_id, item_id) [unique]
  }
}

Table credit_transaction {
  transaction_id int [pk, increment]
  user_id int [ref: > user.user_id, not null]
  amount int [not null, note: 'Positive=earn, Negative=spend']
  transaction_type varchar(50) [not null, note: 'game, minigame, purchase, bonus']
  description varchar(255)
  reference_id int [note: 'Related game/purchase ID']
  reference_type varchar(50)
  created_at datetime [default: `now()`]

  indexes {
    user_id
    created_at
  }
}

Table user_progress {
  progress_id int [pk, increment]
  user_id int [ref: - user.user_id, unique, not null]
  current_level_id int [ref: > progression_level.level_id, not null]
  current_xp int [default: 0]
  games_played int [default: 0]
  games_won int [default: 0]
  updated_at datetime [default: `now()`]
}

// ==========================================
// RF-06: INITIAL RISK IDENTIFICATION (ONBOARDING)
// ==========================================

Table onboarding_question {
  question_id int [pk, incre    ment]
  content text [not null]
  response_type varchar(50) [not null, note: 'multiple_choice, yes_no, scale']
  risk_weight int [default: 1]
  display_order int [not null]
  is_active boolean [default: true]
}

Table answer_option {
  option_id int [pk, increment]
  question_id int [ref: > onboarding_question.question_id, not null]
  content text [not null]
  risk_value int [not null, note: '0=low, 5=high']
  display_order int
}

Table onboarding_response {
  response_id int [pk, increment]
  user_id int [ref: > user.user_id, not null]
  question_id int [ref: > onboarding_question.question_id, not null]
  option_id int [ref: > answer_option.option_id]
  open_answer text
  submitted_at datetime [default: `now()`]

  indexes {
    (user_id, question_id) [unique]
  }
}

Table user_statistic {
  statistic_id int [pk, increment]
  user_id int [ref: > user.user_id, not null]
  metric varchar(100) [not null, note: 'success_rate, avg_time, etc']
  value float [not null]
  calculated_at datetime [default: `now()`]

  indexes {
    (user_id, metric)
  }
}

Table global_statistic {
  statistic_id int [pk, increment]
  metric varchar(100) [not null]
  value float [not null]
  country_id int [ref: > country.country_id]
  calculated_at datetime [default: `now()`]

  indexes {
    (metric, country_id)
  }
}

// ==========================================
// AUDIT AND LOG ENTITIES
// ==========================================

Table activity_log {
  log_id int [pk, increment]
  user_id int [ref: > user.user_id]
  action varchar(100) [not null]
  entity varchar(50)
  entity_id int
  details text
  ip_address varchar(45)
  created_at datetime [default: `now()`]

  indexes {
    user_id
    created_at
  }
}

Table user_session {
  session_id int [pk, increment]
  user_id int [ref: > user.user_id, not null]
  token varchar(500) [not null]
  started_at datetime [default: `now()`]
  expires_at datetime [not null]
  device varchar(255)
  is_active boolean [default: true]

  indexes {
    token
    user_id
  }
}

// ==========================================
// TABLE GROUPS (Visual Organization)
// ==========================================

TableGroup user_core {
  user
  country
  risk_level
}

TableGroup rf01_slang_engine {
  slang
  system_prompt_template
}

TableGroup rf02_simulation {
  scenario
  sensitive_pattern
  game_session
  chat_message
}

TableGroup rf03_pet {
  pet
  pet_state
  user_pet
}

TableGroup rf04_minigames {
  minigame
  swipe_question
  minigame_session
  swipe_response
}

TableGroup rf05_progression {
  progression_level
  cosmetic_item
  user_inventory
  credit_transaction
  user_progress
}

TableGroup rf06_onboarding {
  onboarding_question
  answer_option
  onboarding_response
  user_statistic
  global_statistic
}

TableGroup audit {
  activity_log
  user_session
}
```

---

## Usage Instructions

1. Go to [https://dbdiagram.io](https://dbdiagram.io)
2. Create a new diagram or open an existing one
3. Copy all the DBML code above (inside the ```dbml block)
4. Paste it in the dbdiagram.io editor
5. The diagram will be automatically generated with all relationships

---

## Requirements to Entities Mapping

| Requirement | Involved Entities | TableGroup |
|-------------|-------------------|------------|
| **RF-01** Slang Engine | country, slang, system_prompt_template | rf01_slang_engine |
| **RF-02** AI Simulation | scenario, game_session, chat_message, sensitive_pattern | rf02_simulation |
| **RF-03** Pet | pet, pet_state, user_pet | rf03_pet |
| **RF-04** Minigames | minigame, swipe_question, minigame_session, swipe_response | rf04_minigames |
| **RF-05** Progression | progression_level, cosmetic_item, user_inventory, credit_transaction, user_progress | rf05_progression |
| **RF-06** Onboarding | risk_level, onboarding_question, answer_option, onboarding_response, user_statistic, global_statistic | rf06_onboarding |

---

## Tables Summary (22 total)

| Module | Tables |
|--------|--------|
| User Core | user, country, risk_level |
| Slang Engine | slang, system_prompt_template |
| Simulation | scenario, sensitive_pattern, game_session, chat_message |
| Pet | pet, pet_state, user_pet |
| Minigames | minigame, swipe_question, minigame_session, swipe_response |
| Progression | progression_level, cosmetic_item, user_inventory, credit_transaction, user_progress |
| Onboarding | onboarding_question, answer_option, onboarding_response, user_statistic, global_statistic |
| Audit | activity_log, user_session |

---

## Implementation Notes by Role

| Role | Team Member | Main Tables |
|------|-------------|-------------|
| **Backend/DB** | Wilson | All tables, user_session, activity_log |
| **AI/Backend** | Rafael | system_prompt_template, slang, scenario, chat_message |
| **Frontend** | Alfredo | pet_state (animations <500ms), cosmetic_item |
| **DevOps** | Julio | Optimized indexes already included in schema |
| **Testing** | Marco | sensitive_pattern (validate regex), swipe_question |
