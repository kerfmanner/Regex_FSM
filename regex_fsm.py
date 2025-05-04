from __future__ import annotations
from abc import ABC, abstractmethod
from collections import deque
import string


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

    def check_self(self, char):
        return super().check_self(char)

    def __repr__(self):
        return "StartState"


class TerminationState(State):

    def __init__(self):
        self.next_states = []

    def check_self(self, next_char):
        return True

    def check_next(self, next_char):
        return []

    def __repr__(self):
        return "TerminationState"


class DotState(State):
    """
    state for . character (any character accepted)
    """

    def __init__(self):
        self.next_states = []

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
        return list(all_chars - allowed) if negate else list(allowed)


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

        self.__init_next_state("TERMINATION", prev_states, tmp_next_state, necessary)

    def __init_next_state(
        self,
        next_token: str,
        prev_states: list[State],
        tmp_next_state: State,
        is_necessary: bool,
    ) -> State:
        new_state = None

        match next_token:
            case next_token if next_token.startswith("[") and next_token.endswith("]"):
                new_state = CharacterBracketClassState(next_token)
                if is_necessary:
                    new_prev_states = [tmp_next_state]
                else:
                    new_prev_states = prev_states
                necessary = True
            case next_token if next_token == "TERMINATION":
                new_state = TerminationState()
                if is_necessary:
                    new_prev_states = [tmp_next_state]
                else:
                    new_prev_states = prev_states
                necessary = True
            case next_token if next_token == ".":
                new_state = DotState()
                if is_necessary:
                    new_prev_states = [tmp_next_state]
                else:
                    new_prev_states = prev_states
                necessary = True
            case next_token if next_token == "*":
                new_state = tmp_next_state
                tmp_next_state.next_states.append(tmp_next_state)
                new_prev_states = prev_states + [tmp_next_state]
                necessary = False
            case next_token if next_token == "+":
                new_state = tmp_next_state
                tmp_next_state.next_states.append(tmp_next_state)
                new_prev_states = [tmp_next_state]
                necessary = False
            case next_token if next_token == "?":
                new_state = tmp_next_state
                new_prev_states = prev_states + [tmp_next_state]
                necessary = False
            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)
                if is_necessary:
                    new_prev_states = [tmp_next_state]
                else:
                    new_prev_states = prev_states
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
            1 for i in states for j in i.next_states if isinstance(j, TerminationState)
        )

    @staticmethod
    def get_tokens_from_pattern(regex_pattern):
        stack = deque(list(regex_pattern))
        tokens = []
        while stack:
            token = stack.popleft()
            if token == "[":
                start = "["
                while start != "]" and stack:
                    start = stack.popleft()
                    token += start
                    if not stack:
                        raise ValueError("If pattern has [, it should also have ]")
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
            elif isinstance(state, TerminationState):
                return "Termination"
            else:
                return str(state)

        def get_weight(state: State) -> int:
            if isinstance(state, AsciiState):
                return 'If'+ '(' + state.symbol + ')'
            elif isinstance(state, CharacterBracketClassState):
                return f'If({state.character_class})'
            elif isinstance(state, DotState):
                return 'Any'
            elif isinstance(state, TerminationState):
                return 'Any'
            else:
                return 0

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
                    lines.append(str(state) + ' : '+'None')
                else:
                    lines.append(str(state) + ' : ' + ", ".join(message))

        return '\n'.join(lines)


