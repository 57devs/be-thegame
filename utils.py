import random


def get_game_id(length=8):
	alphabet = '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ' \
			   'abcdefghijkmnopqrstuvwxyz'

	return ''.join(
		[
			random.choice(alphabet)
			for _ in range(length)
		]
	)


def calculate_num_of_q(num_of_questions=10, difficulty=3):

	if difficulty == 1:
		one = int((num_of_questions / 10) * 3)
		two = int(num_of_questions / 10) * 3
		three = int(num_of_questions / 10) * 2
		four = int(num_of_questions / 10) * 1
		five = int(num_of_questions / 10) * 1

	elif difficulty == 3:
		one = int(num_of_questions / 10) * 1
		two = int(num_of_questions / 10) * 3
		three = int(num_of_questions / 10) * 3
		four = int(num_of_questions / 10) * 2
		five = int(num_of_questions / 10) * 1

	elif difficulty == 5:
		one = int(num_of_questions / 10) * 1
		two = int(num_of_questions / 10) * 2
		three = int(num_of_questions / 10) * 2
		four = int(num_of_questions / 10) * 3
		five = int(num_of_questions / 10) * 2

	else:
		one, two, three, four, five = 0, 0, 0, 0, 0

	return [(1, one), (2, two), (3, three), (4, four), (5, five)]
