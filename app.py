import json
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
		difficulty = int(data["difficulty"])
	except:
		return response.json({'error': 'Bad Request'}, status=400)

	if num_of_questions > 25:
		return response.json({'error': 'Maximum question number is 25'})

	questions = DB().get_questions(num_of_questions, difficulty)
	if not questions:
		return response.json({'error': 'Could not retrieve the questions'})

	game_id = get_game_id()
	data['game_id'] = game_id

	DB().create_game(game_id, game_name, username, questions)
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
		players = DB().get_players_by_game_id(game_id)
		if username in players:
			return response.json({'error': 'A user with that name already exists.'})
		DB().add_player(username, game_id)

		return response.json({'success': 'Player has joined.'})

	return response.json({'error': 'Bad Request'}, status=400)


@app.route('/start-game/<game_id>', methods=['GET'])
async def game_started(request, game_id):
	game = DB().get_game(game_id)
	if not game:
		return response.json({'error': 'Game could not be found.'}, status=404)
	DB().set_game_started(game_id)
	return response.json({'success': 'Game ID: ' + game_id + ' is now marked as started'})


@app.route('/games/<game_id>/players/<player>/score', methods=['POST'])
async def player_result(request, game_id, player):
	try:
		data = request.json
	except:
		return response.json({'error': 'Bad Request'}, status=400)

	game = DB().get_game(game_id)
	if not game:
		return response.json({'error': 'Game not found.'}, status=404)

	players = DB().get_players_by_game_id(game_id)
	if player not in players:
		return response.json({'error': 'Player not found'}, status=404)

	DB().set_player_score(game_id, player, data)
	return response.json({'success': 'Player score updated'}, status=200)


@app.route('/games/<game_id>/scoreboard', methods=['GET'])
async def game_result(request, game_id):
	game = DB().get_game(game_id)
	if not game:
		return response.json({'error': 'Game not found.'}, status=404)

	player_scores = DB().get_player_scores_by_game_id(game_id)
	data = {'game_name': game['game_name'], 'created_by': game['created_by'], 'player_scores': []}

	for username, score in player_scores:
		data['player_scores'].append({username: score if score else 0})

	return response.json(data)


@app.websocket('/ws/<game_id>')
async def feed(request, ws, game_id):
	game = DB().get_game(game_id)
	if not game:
		await ws.send(response.json({'error': 'game not found'}))
	while True:

		try:
			await asyncio.wait_for(ws.recv(), timeout=0.1)
			game_started = ws.recv()
			if game_started:
				DB().set_game_started(game_id)
		except:
			pass

		players = DB().get_players_by_game_id(game_id)
		game = DB().get_game(game_id)
		data = {
			'players': players,
			'game_name': game['game_name'],
			'created_by': game['created_by'],
			'questions': game['questions'],
			'started': game['started']
		}

		await ws.send(json.dumps(data))
		await asyncio.sleep(1)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)
