import sys
import sqlite3
import json
from builtins import object

connection = sqlite3.connect('db.db')
cursor = connection.cursor()


class DB(object):
	def __init__(self):
		self.cursor = connection.cursor()

	def create_tables(self):
		create_table = f"CREATE TABLE IF NOT EXISTS games(game_id TEXT UNIQUE, game_name TEXT, created_by TEXT, " \
					   f"questions TEXT, game_started INTEGER, game_ended INTEGER)"
		self.cursor.execute(create_table)

		create_table = f"CREATE TABLE IF NOT EXISTS players(username TEXT, game_id TEXT," \
					   f"score INTEGER, extras TEXT, is_ready INTEGER," \
					   f"CONSTRAINT fk_game_id FOREIGN KEY (game_id) REFERENCES games(game_id)" \
					   f"ON DELETE CASCADE)"
		self.cursor.execute(create_table)

		create_table = f"CREATE TABLE IF NOT EXISTS questions(" \
					   f"question_id INTEGER PRIMARY KEY AUTOINCREMENT, " \
					   f"title TEXT, choices TEXT, correct_choice INTEGER, " \
					   f"difficulty INTEGER)"
		self.cursor.execute(create_table)

	def drop_tables(self):
		self.cursor.execute(
			f"DROP TABLE games"
		)
		self.cursor.execute(
			f"DROP TABLE players"
		)
		connection.commit()

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
			q_id = question[0]
			title = question[1]
			choices = json.loads(question[2])
			correct_choice = question[3]
			difficulty = question[4]
			question_list.append({
				'q_id': q_id,
				'title': title,
				'choices': choices,
				'correct_choice': correct_choice,
				'difficulty': difficulty,
			})

		return question_list

	def create_game(self, game_id, game_name, created_by, questions):
		param = [game_id, game_name, created_by, json.dumps(questions), 0]
		self.cursor.execute(
			f"INSERT INTO games (game_id, game_name, created_by, questions, game_started)"
			f"VALUES (?,?,?,?,?)", param)
		connection.commit()

	def get_game(self, game_id):
		game = self.cursor.execute(
			f"SELECT * FROM games WHERE game_id=:game_id limit 1", {'game_id': game_id}
		)

		data = {}
		game = game.fetchone()
		if game is not None:
			game_id = game[0]
			game_name = game[1]
			created_by = game[2]
			questions = game[3]
			started = game[4]
			data = {
				'game_id': game_id,
				'game_name': game_name,
				'created_by': created_by,
				'questions': json.loads(questions),
				'started': started
			}

		return data

	def add_player(self, username, game_id):
		player = self.cursor.execute(
			f"SELECT username FROM players WHERE username=:username AND game_id=:game_id",
			{'username': username, 'game_id': game_id}
		)

		if not player.fetchone():
			self.cursor.execute(
				f"INSERT INTO players (username, game_id) VALUES (?,?)", [username, game_id]
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
			f"UPDATE games SET game_started=1 WHERE game_id=:game_id",
			{'game_id': game_id}
		)
		connection.commit()

	def set_game_ended(self, game_id):
		self.cursor.execute(
			f"UPDATE games SET game_ended=1 WHERE game_id=:game_id",
			{'game_id': game_id}
		)
		connection.commit()

	def set_player_score(self, game_id, username, extras):
		score = extras['total_score']
		self.cursor.execute(
			f"UPDATE players SET score=:score, extras=:extras "
			f"WHERE game_id=:game_id AND username=:username",
			{'score': score, 'extras': json.dumps(extras), 'game_id': game_id, 'username': username}
		)
		connection.commit()

	def get_player_scores_by_game_id(self, game_id):
		player_scores = self.cursor.execute(
			f"SELECT username, score FROM players WHERE game_id=:game_id",
			{'game_id': game_id}
		)

		return player_scores.fetchall()

	def get_lobby_games(self):
		lobby_games = self.cursor.execute(
			f"SELECT * FROM games WHERE game_started=0 AND game_ended=0"
		)
		return lobby_games.fetchall()

	def set_player_ready(self, game_id, username, is_ready):
		self.cursor.execute(
			f"UPDATE players SET is_ready=:is_ready WHERE game_id=:game_id AND username=:username",
			{'is_ready': is_ready, 'game_id': game_id, 'username': username}
		)
		connection.commit()

	def remove_player_from_game(self, game_id, username):
		self.cursor.execute(
			f"DELETE FROM players WHERE game_id=:game_id AND username=:username",
			{'game_id': game_id, 'username': username}
		)
		connection.commit()


if __name__ == '__main__':
	if len(sys.argv) == 2:
		if sys.argv[1] == "tabloSil":
			DB().drop_tables()
		if sys.argv[1] == "soruDoldur":
			DB().fill_questions()
		if sys.argv[1] == "createTables":
			DB().create_tables()
