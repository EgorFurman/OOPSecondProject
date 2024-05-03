from random import randint
from typing import Any
from itertools import chain


class Cell:
    __STRING_REPRESENT = {0: ' ', 1: 'X', 2: 'O'}

    def __init__(self):
        self.value = 0

    def is_empty(self):
        return self.value == 0

    def is_field(self):
        return self.value != 0

    def __bool__(self) -> bool:
        return not self.value

    def __str__(self):
        return self.__STRING_REPRESENT[self.value]


class BoolDescriptor:
    def __set_name__(self, owner, name):
        self.name = f'_{owner}__{name}'

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
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

        self.is_human_win = False
        self.is_computer_win = False
        self.is_draw = False

    def __getitem__(self, item):
        row, col = item
        self.__verify_indices(row, col)

        return self.__pole[row][col].value

    def __setitem__(self, key, value):
        row, col = key
        self.__verify_indices(row, col)

        self.__pole[row][col].value = value

        columns = self.__get_columns()

        self.is_human_win = any(all(cell.value == self.HUMAN_X for cell in line) for line in columns)
        self.is_computer_win = any(all(cell.value == self.COMPUTER_O for cell in line) for line in columns)
        self.is_draw = not self.is_human_win and not self.is_computer_win and not any(cell for cell in chain(*self.__pole))

    def __bool__(self):
        return not (self.is_human_win or self.is_computer_win or self.is_draw)

    def init(self) -> None:
        for cell in chain(*self.__pole):
            cell.value = self.FREE_CELL

        self.is_human_win = False
        self.is_computer_win = False
        self.is_draw = False

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

    def human_go(self):
        self[self.__get_user_step()] = self.HUMAN_X

    def computer_go(self) -> None:
        columns = self.__get_columns()

        is_not_cell = lambda cell: not cell

        for column in columns:
            filled_cells = list(filter(is_not_cell, column))

            if len(filled_cells) == 2 and all(map(lambda cell: cell.value==self.COMPUTER_O, filled_cells)):
                for cell in column:
                    if cell:
                        cell.value = self.COMPUTER_O
                        self.is_computer_win = any(
                            all(cell.value == self.COMPUTER_O for cell in line) for line in columns)
                        return

        for column in columns:
            filled_cells = list(filter(is_not_cell, column))

            if len(filled_cells) == 2 and all(map(lambda cell: cell.value == self.HUMAN_X, filled_cells)):
                for cell in column:
                    if cell:
                        cell.value = self.COMPUTER_O
                        self.is_computer_win = any(
                            all(cell.value == self.COMPUTER_O for cell in line) for line in columns)
                        return

        if self.__pole[1][1]:
            self[1, 1] = self.COMPUTER_O
            return

        for row, col in ((0, 0), (0, 2), (2, 0), (2, 2)):
            if self.__is_free_cell(row, col):
                self[row, col] = self.COMPUTER_O
                return

        while True:
            row, col = randint(0, 2), randint(0, 2)
            if self.__is_free_cell(row, col):
                self[row, col] = self.COMPUTER_O
                return

    def __get_user_step(self) -> tuple[int, int]:
        while True:
            res = input(r'''Введите две цифры соответствующие координате свободной клетки через запятую. 
В порядке: строка(указано слева), столбец(указано сверху): ''')

            try:
                step = tuple(map(lambda x: int(x.strip()) - 1, res.split(',')))
                self.__verify_indices(*step)

                if not self.__is_free_cell(*step):
                    raise IndexError('Указанная клетка уже занята.')
            except IndexError as ex:
                print(ex)
                continue
            except Exception:
                print('неверный формат введенных данных.')
                continue

            return step

    def __verify_indices(self, row: Any, col: Any) -> None:
        if not self.__is_game_cell_coordinates(row, col):
            raise IndexError('Клетка с указанными индексами не существует.')

    def __get_columns(self) -> tuple:
        row1, row2, row3 = (row for row in self.__pole)
        col1, col2, col3 = (tuple(row[i] for row in self.__pole) for i in range(3))
        main_dig, side_dig = tuple(self.__pole[i][i] for i in range(3)), tuple(self.__pole[i][-1 - i] for i in range(3))
        return row1, row2, row3, col1, col2, col3, main_dig, side_dig

    def __is_free_cell(self, row: int, col: int) -> bool:
        return self.__pole[row][col].is_empty()

    @staticmethod
    def __is_game_cell_coordinates(row: int, col: int) -> bool:
        return (type(row) is int and type(col) is int) and row in range(3) and col in range(3)


if __name__ == '__main__':
    game = TicTacToe()
    game.init()
    step_game = 0
    while game:
        game.show()

        if step_game % 2 == 0:
            game.human_go()
        else:
            game.computer_go()

        step_game += 1

    game.show()

    if game.is_human_win:
        print("Поздравляем! Вы победили!")
    elif game.is_computer_win:
        print("Все получится, со временем")
    else:
        print("Ничья.")