from __future__ import annotations

import string
from abc import ABC, abstractmethod
from collections import deque


class State(ABC):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        return [state for state in self.next_states if state.check_self(next_char)]


class StartState(State):

    def __init__(self):
        self.next_states = []
        self.is_termination = False

    def check_self(self, char):
        return super().check_self(char)

    def __repr__(self):
        return "StartState"

class DotState(State):
    """
    state for . character (any character accepted)
    """

    def __init__(self):
        self.next_states = []
        self.is_termination = False

    def check_self(self, char: str):
        return True

    def __repr__(self):
        return "DotState"


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """

    def __init__(self, symbol: str) -> None:
        self.next_states = []
        self.symbol = symbol
        self.is_termination = False

    def check_self(self, curr_char: str) -> bool:
        return curr_char == self.symbol

    def __repr__(self):
        return f"AsciiState for {self.symbol}"


class CharacterBracketClassState(State):
    """
    State for Regex Character Bracket Class
    """

    def __init__(self, character_class):
        """
        Character class = '[{Ascii}-{Ascii}]'
        """
        self.next_states = []
        self.character_class = character_class
        self.symbols = self.get_symbols_from_class(character_class)
        self.is_termination = False

    def check_self(self, char):
        for symbol in self.symbols:
            if symbol == char:
                return True
        return False

    def __repr__(self):
        return f"CharacterClassState: {self.character_class}"

    @staticmethod
    def get_symbols_from_class(char_class):
        """
        Get symbols that can be used from [...] regex token.
        """
        if not (char_class.startswith("[") and char_class.endswith("]")):
            raise ValueError("Input must be in the format [..]")

        content = char_class[1:-1]
        negate = False
        if content.startswith("^"):
            negate = True
            content = content[1:]

        allowed = set()
        i = 0
        while i < len(content):
            if i + 2 < len(content) and content[i + 1] == "-":
                start, end = content[i], content[i + 2]
                allowed.update(chr(c) for c in range(ord(start), ord(end) + 1))
                i += 3
            else:
                allowed.add(content[i])
                i += 1

        all_chars = set(string.printable)
        return (all_chars - allowed) if negate else (allowed)


class RegexFSM:

    def __init__(self, regex_expr: str) -> None:

        self.curr_state = StartState()
        tokens = self.get_tokens_from_pattern(regex_expr)
        prev_states = [self.curr_state]
        tmp_next_state = self.curr_state
        necessary = True

        for token in tokens:
            new_prev_states, tmp_next_state, necessary = self.__init_next_state(
                token, prev_states, tmp_next_state, necessary
            )
            prev_states = new_prev_states

        if necessary:
            tmp_next_state.is_termination = True
        else:
            for state in new_prev_states:
                state.is_termination = True

    def __init_next_state(
        self,
        next_token: str,
        prev_states: list[State],
        last_created_state: State,
        is_necessary: bool,
    ) -> State:
        new_state = None

        match next_token:
            case next_token if next_token.startswith("[") and next_token.endswith("]"):
                new_state = CharacterBracketClassState(next_token)
                new_prev_states = [last_created_state] if is_necessary else prev_states
                necessary = True
            case next_token if next_token == ".":
                new_state = DotState()
                new_prev_states = [last_created_state] if is_necessary else prev_states
                necessary = True
            case next_token if next_token == "*":
                new_state = last_created_state
                last_created_state.next_states.append(last_created_state)
                new_prev_states = prev_states + [last_created_state]
                necessary = False
            case next_token if next_token == "+":
                new_state = last_created_state
                if is_necessary:
                    new_prev_states = [last_created_state]
                    last_created_state.next_states.append(last_created_state)
                else:
                    new_prev_states = prev_states
                necessary = False
            case next_token if next_token == "?":
                new_state = last_created_state
                new_prev_states = prev_states + [last_created_state] if is_necessary else prev_states
                necessary = False
            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)
                new_prev_states = [last_created_state] if is_necessary else prev_states
                necessary = True
            case _:
                raise AttributeError("Character is not supported")

        if necessary:
            for state in new_prev_states:
                state.next_states.append(new_state)

        return new_prev_states, new_state, necessary

    def check_string(self, message: str):
        if not isinstance(message, str):
            raise ValueError("Regex pattern should be string")

        states = [self.curr_state]
        for char in message:
            new_states = []

            for state in states:
                new_states.extend(state.check_next(char))

            states = new_states
        return any(
            1 for i in states if i.is_termination
        )

    @staticmethod
    def get_tokens_from_pattern(regex_pattern):
        stack = deque(list(regex_pattern))
        tokens = []
        while stack:
            token = stack.popleft()
            if token == "[":
                start = token
                while start != "]":
                    if not stack:
                        raise ValueError("If pattern has [, it should also have ], or the character class has no characters.")
                    start = stack.popleft()
                    token += start


            tokens.append(token)
        return tokens

    def to_dot_file(self) -> str:

        def get_node_label(state: State) -> str:
            if isinstance(state, AsciiState):
                return f"Ascii('{state.symbol}')"
            elif isinstance(state, CharacterBracketClassState):
                return f"CharClass('{state.character_class}')"
            elif isinstance(state, DotState):
                return "Dot"
            elif isinstance(state, StartState):
                return "Start"
            else:
                return str(state)

        def get_weight(state: State) -> int:
            if isinstance(state, AsciiState):
                return "If" + "(" + state.symbol + ")"
            elif isinstance(state, CharacterBracketClassState):
                return f"If({state.character_class})"
            elif isinstance(state, DotState):
                return "Any()"
            else:
                return 'ERROR'

        state_ids = {}
        dot_lines = ["digraph FSM {"]
        queue = deque([self.curr_state])
        visited = set()
        node_id = 0

        while queue:
            current = queue.popleft()
            if id(current) in visited:
                continue
            visited.add(id(current))

            if current not in state_ids:
                state_ids[current] = f"node{node_id}"
                node_id += 1

            node_label = get_node_label(current)
            if current.is_termination:
                dot_lines.append(f'{state_ids[current]} [label="{node_label}", peripheries=2];')
            else:
                dot_lines.append(f'{state_ids[current]} [label="{node_label}"];')
            for next_state in current.next_states:
                if next_state not in state_ids:
                    state_ids[next_state] = f"node{node_id}"
                    node_id += 1

                weight = get_weight(next_state)
                queue.append(next_state)
                dot_lines.append(
                    f'{state_ids[current]} -> {state_ids[next_state]} [label="{weight}"];'
                )

        dot_lines.append("}")
        return "\n".join(dot_lines)

    # This was used during debugging.
    def __repr__(self):
        stack = [self.curr_state]
        visited = set()
        lines = []
        while stack:
            state = stack.pop()
            if id(state) not in visited:
                message = []
                for connect in state.next_states:
                    message.append(str(connect))
                    stack.append(connect)
                visited.add(id(state))
                if not message:
                    lines.append(str(state) + " : " + "None")
                else:
                    lines.append(str(state) + " : " + ", ".join(message))

        return "\n".join(lines)

pattern = 'ab*[0-9]?d*e+E'
regex_compiler = RegexFSM(pattern)
print(regex_compiler.to_dot_file())