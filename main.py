from random import randint, shuffle, choice
from itertools import chain


class Cell:
    __STRING_REPRESENT = {0: ' ', 1: 'X', 2: 'O'}

    def __init__(self):
        self.value = 0

    def __str__(self):
        return self.__STRING_REPRESENT[self.value]

    def is_empty(self):
        return self.value == 0

    def is_field(self):
        return self.value != 0


class BoolDescriptor:
    def __set_name__(self, owner, name):
        self.name = f'_{owner}__{name}'

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value: bool):
        if not isinstance(value, bool):
            raise ValueError('Значение')
        setattr(instance, self.name, value)


class TicTacToe:
    FREE_CELL = 0  # свободная клетка
    HUMAN_X = 1  # крестик (игрок - человек)
    COMPUTER_O = 2  # нолик (игрок - компьютер)

    is_human_win = BoolDescriptor()
    is_computer_win = BoolDescriptor()
    is_draw = BoolDescriptor()

    def __init__(self):
        self.__pole = tuple(tuple(Cell() for _ in range(3)) for _ in range(3))

        self.__lines = self.__get_lines()

        self.is_human_win = False
        self.is_computer_win = False
        self.is_draw = False

    def __getitem__(self, item):
        row, col = item
        self.__verify_coords(row, col)

        return self.__pole[row][col].value

    def __setitem__(self, key, value):
        row, col = key
        self.__verify_coords(row, col)

        self.__pole[row][col].value = value

    def play(self):
        step_game = 0

        while not (self.is_draw or self.is_human_win or self.is_computer_win):
            self.show()

            if step_game % 2 == 0:
                game.human_go()
            else:
                game.computer_go()
            step_game += 1

            if self.__is_win():
                self.is_human_win = self.__is_winner(player_sign=self.HUMAN_X)
                self.is_computer_win = not self.is_human_win
            self.is_draw = self.__is_draw()

        self.show()

        if game.is_human_win:
            print("The future is not set. There is no fate but what we make for ourselves.")
        elif game.is_computer_win:
            print("You are terminated.")
        else:
            print("Cyborgs don't feel pain. You do.")

        self.__init__()

    def show(self) -> None:
        # Выводим верхнюю горизонтальную линию
        print("    " + "   ".join(str(i + 1) for i in range(len(self.__pole))))
        print("  " + "┌───" * (len(self.__pole)) + "┐")

        for i, row in enumerate(self.__pole):
            # Выводим индекс строки
            print("{} │".format(i + 1), end="")

            # Выводим содержимое строки и вертикальные разделители
            for cell in row:
                print(" {} │".format(cell), end="")
            print()

            # Выводим горизонтальные разделители между строками
            if i < len(self.__pole) - 1:
                print("  " + "├───" * (len(self.__pole)) + "┤")

        # Выводим нижнюю горизонтальную линию
        print("  " + "└───" * (len(self.__pole)) + "┘")

    def human_go(self) -> None:
        self[self.__get_user_step()] = self.HUMAN_X

    def __get_user_step(self) -> tuple[int, int]:
        while True:
            res = input(r'''Введите две цифры соответствующие координате свободной клетки через запятую. 
В порядке: строка(указано слева), столбец(указано сверху): ''')

            try:
                step = tuple(map(lambda x: int(x.strip()) - 1, res.split(',')))
                self.__verify_coords(*step)
                if not self[*step] == self.FREE_CELL:
                    raise IndexError('Указанная клетка уже занята.')
            except IndexError as ex:
                print(ex)
                continue
            except Exception:
                print('Неверный формат введенных данных.')
                continue
            return step

    def __try_grab_victory(self) -> bool:
        angle_cells = [(0, 0), (0, 2), (2, 0), (2, 2)]
        shuffle(angle_cells)

        for column in self.__lines:
            filled_cells = list(filter(lambda cell: cell.is_field(), column))

            if len(filled_cells) == 2 and all(map(lambda cell: cell.value == self.COMPUTER_O, filled_cells)):
                for cell in column:
                    if cell.is_empty():
                        cell.value = self.COMPUTER_O
                        return True
        return False

    def __try_block_human(self) -> bool:
        for column in self.__lines:
            filled_cells = list(filter(lambda cell: cell.is_field(), column))

            if len(filled_cells) == 2 and all(map(lambda cell: cell.value == self.HUMAN_X, filled_cells)):
                for cell in column:
                    if cell.is_empty():
                        cell.value = self.COMPUTER_O
                        return True
        return False

    def __try_occupy_center(self) -> bool:
        if self[1, 1] == self.FREE_CELL:
            self[1, 1] = self.COMPUTER_O
            return True
        return False

    def __try_occupy_corner(self) -> bool:
        angle_cells = [(0, 0), (0, 2), (2, 0), (2, 2)]
        shuffle(angle_cells)

        for row, col in angle_cells:
            if self[row, col] == self.FREE_CELL:
                self[row, col] = self.COMPUTER_O
                return True
            return False

    def __try_occupy_random_free_cell(self) -> bool:
        while True:
            row, col = randint(0, 2), randint(0, 2)
            if self[row, col] == self.FREE_CELL:
                self[row, col] = self.COMPUTER_O
                return True
            return False

    def computer_go(self):
        if self.__try_grab_victory():
            return
        elif self.__try_block_human():
            return
        elif self.__try_occupy_center():
            return
        elif self.__try_occupy_corner():
            return
        else:
            self.__try_occupy_random_free_cell()

    def __is_win(self) -> bool:
        return any(all(c.is_field() and c.value == line[0].value for c in line) for line in self.__lines)

    def __is_winner(self, player_sign) -> bool:
        for line in self.__lines:
            if all(cell.value == player_sign for cell in line):
                return True
        return False

    def __is_draw(self):
        return all(cell.is_field() for cell in chain(*self.__pole))

    def __verify_coords(self, row: int, col: int) -> None:
        if not (self.__is_valid_coord(row) and self.__is_valid_coord(col)):
            raise IndexError('Клетка с указанными индексами не существует.')

    def __get_lines(self) -> tuple:
        row1, row2, row3 = (row for row in self.__pole)
        col1, col2, col3 = (tuple(row[i] for row in self.__pole) for i in range(3))
        main_dig, side_dig = tuple(self.__pole[i][i] for i in range(3)), tuple(self.__pole[i][-1 - i] for i in range(3))
        return row1, row2, row3, col1, col2, col3, main_dig, side_dig

    @staticmethod
    def __is_valid_coord(coord: int) -> bool:
        return type(coord) is int and coord in range(3)


if __name__ == '__main__':
    game = TicTacToe()
    game.play()
