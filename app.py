import asyncio

from sanic import Sanic, response
from sanic_cors import CORS

from db import DB
from utils import get_game_id

db = {}
app = Sanic(__name__)
CORS(app)


@app.route('/question/fill', methods=['GET', 'POST'])
async def fill(request):
	DB().fill_questions()


@app.route('/create-game', methods=['POST'])
async def create_game(request):
	try:
		data = request.json
		username = data["username"]
		game_name = data["game_name"]
		num_of_questions = int(data["num_of_questions"])
	except:
		return response.json({'error': 'Bad Request'}, status=400)

	if num_of_questions > 25:
		return response.json({'error': 'Maximum question number is 25'})
	questions = DB().get_questions(num_of_questions)
	if not questions:
		return response.json({'error': 'Could not retrieve the questions'})

	data = {
		'questions': []
	}

	for question in questions:
		question_data = {
			'question': question['title'],
			'choices': {
				'choice_a': question['choices'][0],
				'choice_b': question['choices'][1],
				'choice_c': question['choices'][2],
				'choice_d': question['choices'][3]
			},
			'correct_choice': question['correct_choice'],
			'difficulty': question['difficulty']
		}
		data['questions'].append(question_data)

	game_id = get_game_id()
	data['game_id'] = game_id

	DB().create_game(game_id, game_name, username)
	DB().add_player(username, game_id)

	return response.json(data)


@app.route('/join/<game_id>', methods=['POST'])
async def join_game(request, game_id):
	try:
		data = request.json
		username = data['username']
	except:
		return response.json({'error': 'Bad Request'}, status=400)

	game = DB().get_game(game_id)
	if not game:
		return response.json({'error': 'Game could not be found.'}, status=404)

	if game['started'] == 1:
		return response.json({'error': 'Game has already started.'}, status=403)  # 403 olur mu?

	if username:
		DB().add_player(username, game_id)

		return response.json({'success': 'Player has joined.'})

	return response.json({'error': 'Bad Request'}, status=400)


@app.websocket('/ws/<game_id>')
async def feed(request, ws, game_id):
	game = DB().get_game(game_id)
	if not game:
		await ws.send(response.json({'error': 'game not found'}))
	while True:
		players = DB().get_players_by_game_id(game_id)

		data = {
			'players': players,
			'game_name': game['game_name'],
			'created_by': game['created_by']
		}

		await ws.send(response.json(data))
		await asyncio.sleep(1)

		game_started = await ws.recv()
		if game_started:
			DB().set_game_started(game_id)


if __name__ == '__main__':
	app.run()
