import random
from replit import clear
from art import logo

cards = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]

def deal_card():
  return random.choice(cards)

def calculate_score(lst):
  if sum(lst) == 21:
    return 0
  
  elif 11 in lst:
    if sum(lst) > 21:
      lst.remove(11)
      lst.append(1)
  
  return sum(lst)

def compare(us, cs):
  if us == cs:
    return 'It\'s a draw. 🙃\n\n'
  elif cs in [0, 21]:
    return 'Computer wins due to blackjack. 😥\n\n'
  elif us in [0, 21]:
    return 'You win due to blackjack. 😎\n\n'
  elif us > 21:
    return 'You lost due to going over. 😓\n\n'
  elif cs > 21:
    return 'Computer lost due to going over. 😂\n\n'
  else:
    if us > cs:
      return 'You win due to higher score. 😄\n\n'
    else:
      return 'Computer wins due to higher score. 😭\n\n'
    
def play_game():
  
  print(logo)
  
  user_cards = []
  computer_cards = []
  
  for _ in range(2):
    user_cards.append(deal_card())
    computer_cards.append(deal_card())

  user_score = calculate_score(user_cards)
  comp_score = calculate_score(computer_cards)

  print(f'Your hand is {user_cards} and score is {user_score}.\n')
  print(f'Computer\'s first card is {computer_cards[1]}.\n\n')
  
  condition = True
  while condition:
    if (comp_score == 0) or (user_score > 21) or (user_score == 0) or (comp_score > 21):
      print(compare(user_score, comp_score))
      condition = False
    else:
      if input('Do you want to draw another card? Type "y" or "n": ') == 'y':
        print('You drew another card.\n')
        user_cards.append(deal_card())
        user_score = calculate_score(user_cards)
        print(f'Your hand is {user_cards} and score is {user_score}.\n')
      else:
        while comp_score < 17:
          print('\nComputer drew another card.\n')
          computer_cards.append(deal_card())
          comp_score = calculate_score(computer_cards)
          print(f'Computer\'s non-hidden cards are {computer_cards[1:]}.\n')
        print('\n', compare(user_score, comp_score))
        condition = False

  print(f'Computer\'s final hand was {computer_cards} and final score was {comp_score}.\n')
  
  while input('Do you want to play a game of Blackjack? "y" or "n": ') == 'y':
  clear()
  play_game()
