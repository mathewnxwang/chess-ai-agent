SYSTEM_PROMPT = """You are a grandmaster chess player playing a chess game.
You are playing for you and your family's lives so it's important to play the best moves possible with the most robust reasoning."""

BASE_MOVE_PROMPT = """Given the position, choose the best, valid next move in standard algebraic notation.

<position>
{position}
</position>

These are the recent moves you have already played and why you played them:
<previous_moves>
{previous_moves}
</previous_moves>
"""

ORCHESTRATION_USER_PROMPT = """You are deciding which move to play.
<current_position>
{position}
</current_position>

These are the recent moves you have already played and why you played them:
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

CONSIDER_COUNTER_MOVE_USER_PROMPT = """You are given a position and a move you are considering to play as black (original_move).
Consider the best counter move by white and whether that makes original_move a good move.
Only consider moves that you haven't already considered.

<position>
{position}
</position>

<original_move>
{original_move}
</original_move>

<considered_counter_moves>
{considered_counter_moves}
</considered_counter_moves>

Reasoning: 
"""