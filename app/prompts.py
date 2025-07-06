SYSTEM_PROMPT = """You are a grandmaster chess player playing a chess game.
You are playing for you and your family's lives so it's important to play the best moves possible with the most robust reasoning."""

ORCHESTRATION_USER_PROMPT = """You are deciding which move to play.
<current_position>
{position}
</current_position>

These are the moves you have already played and why you played them:
<previous_moves>
{previous_moves}
</previous_moves>

These are your thoughts on the existing position and which move to play:
<considered_moves>
{considered_moves}
</considered_moves>

Decide whether you want to want to consider a new move or if you're ready to decide on a move.

Consider a new move if you haven't already considered at least two moves."""

CONSIDER_NEW_MOVE_USER_PROMPT = """{base_move_prompt}

Here are other moves you already considered. DO NOT CHOOSE FROM THESE MOVES:
<considered_moves>
{considered_moves}
</considered_moves>

Move: """

DECIDE_ON_MOVE_USER_PROMPT = """{base_move_prompt}

Here is your reasoning for why you were ready to decide on a move:
<decision_reasoning>
{decision_reasoning}
</decision_reasoning>

Here are all of the moves to consider. ONLY CHOOSE FROM THESE MOVES:
<considered_moves>
{considered_moves}
</considered_moves>

Move: """

BASE_MOVE_PROMPT = """Given the position in PGN format, choose the best, valid next move in standard algebraic notation.

<additional_instructions>
- Example of a correct response: 'e5'
- Examples of incorrect responses:
  - '2. e5'
  - 'e5 is the best move to play in this position.'
- For the love of god please don't add prefixes like '2.' or '2... ' to your move.
- Black to play.
</additional_instructions>

<position>
{position}
</position>

These are the recent moves you have already played and why you played them:
<previous_moves>
{previous_moves}
</previous_moves>
"""