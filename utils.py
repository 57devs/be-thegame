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
