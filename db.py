import json
import sqlite3
from builtins import object

connection = sqlite3.connect('db.db')
cursor = connection.cursor()

create_table = f"CREATE TABLE IF NOT EXISTS games(game_id TEXT UNIQUE, game_name TEXT, created_by TEXT, " \
			   f"game_started INTEGER)"
cursor.execute(create_table)

create_table = f"CREATE TABLE IF NOT EXISTS players(username TEXT, game_id TEXT," \
			   f"CONSTRAINT fk_game_id FOREIGN KEY (game_id) REFERENCES games(game_id)" \
			   f"ON DELETE CASCADE)"
cursor.execute(create_table)

create_table = f"CREATE TABLE IF NOT EXISTS questions(" \
			   f"question_id INTEGER PRIMARY KEY AUTOINCREMENT, " \
			   f"title TEXT, choices TEXT, correct_choice INTEGER, " \
			   f"difficulty INTEGER)"
cursor.execute(create_table)


class DB(object):
	def __init__(self):
		self.cursor = connection.cursor()

	def fill_questions(self):
		with open('questions.json') as questions:
			questions = json.load(questions)
			for question in questions:
				title = question['q']
				choices = json.dumps(question['c'])
				correct_choice = question['co']
				difficulty = int(question['r'])
				query = [title, choices, correct_choice, difficulty]

				self.cursor.execute(f"INSERT INTO questions (title, choices, correct_choice, difficulty) "
									f"VALUES (?,?,?,?)", query)
				connection.commit()

	def get_questions(self, num_of_questions, difficulty):
		get_questions = f"SELECT * FROM questions WHERE difficulty=:difficulty ORDER BY RANDOM() LIMIT '{num_of_questions}'"
		question_db = cursor.execute(get_questions, {'difficulty': difficulty})
		questions = question_db.fetchall()
		question_list = []

		for question in questions:
			title = question[1]
			choices = json.loads(question[2])
			correct_choice = question[3]
			difficulty = question[4]
			question_list.append({
				'title': title,
				'choices': choices,
				'correct_choice': correct_choice,
				'difficulty': difficulty,
			})

		return question_list

	def create_game(self, game_id, game_name, created_by):
		create_game = f"INSERT INTO games (game_id, game_name, created_by, game_started)" \
					  f"VALUES ('{game_id}', '{game_name}', '{created_by}', 0)"
		self.cursor.execute(create_game)
		connection.commit()

	def get_game(self, game_id):
		game = self.cursor.execute(
			f"SELECT * FROM games WHERE game_id=:game_id limit 1", {'game_id': game_id}
		)

		game = game.fetchone()
		game_id = game[0]
		game_name = game[1]
		created_by = game[2]
		started = game[3]
		data = {'game_id': game_id, 'game_name': game_name, 'created_by': created_by, 'started': started}
		return data

	def add_player(self, username, game_id):
		player = self.cursor.execute(
			f"SELECT username FROM players WHERE username=:username AND game_id=:game_id",
			{'username': username, 'game_id': game_id}
		)

		if not player.fetchone():
			self.cursor.execute(
				f"INSERT INTO players (username, game_id) VALUES ('{username}', '{game_id}')"
			)
			connection.commit()

	def get_players_by_game_id(self, game_id):
		players = self.cursor.execute(
			f"SELECT * FROM players WHERE game_id=:game_id", {'game_id': game_id}
		)

		players_tuple = players.fetchall()
		players_list = []

		for player in players_tuple:
			players_list.append(player[0])

		return players_list

	def set_game_started(self, game_id):
		self.cursor.execute(
			f"UPDATE games SET game_started = 1 WHERE game_id=:game_id",
			{'game_id': game_id}
		)
		connection.commit()


if __name__ == '__main__':
	DB().create_game('ABsC', 'burcuoyun', 'burcu')
	print(DB().get_game('ABsC'))

	DB().add_player('emircan', 'ABsC')
	DB().add_player('yucehan', 'ABsC')
	DB().add_player('ferhat', 'ABsC')

	for player in DB().get_players_by_game_id('ABsC'):
		print(player)

	print(DB().get_game('ABsC'))
