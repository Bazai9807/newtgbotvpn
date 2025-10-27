from sqlalchemy import insert, select, update, delete
from sqlalchemy.orm import Session

from config_bd.BaseModel import engine, users


class SQL:
    session = Session(engine)

    def INSERT(self, user_id: int, Is_pay_null: bool, Is_tarif: bool = False, ref: str = '', is_delete: bool = False):
        """
        Добавляет пользователей в БД users.
        """

        ins = insert(users).values(
                    User_id=user_id,
                    Ref=ref,
                    Is_delete=is_delete,
                    Is_pay_null=Is_pay_null,
                    Is_tarif=Is_tarif
                )
        self.session.execute(ins)
        self.session.commit()

    def SELECT_ID(self, user_id):
        """
        Проверяет наличие пользователя в БД user и возвращает строку таблицы или NONE
        :param user_id: int
        :return: row | None
        """
        s = select(users).where(users.c.User_id == user_id)
        re = self.session.execute(s)
        result = re.fetchone()
        return result

    def SELECT_REF(self, user_id):
        """
        Проверяет наличие у пользователя тригера пробной подписки
        :param user_id: int
        :return: row | None
        """
        s = select(users).where(users.c.User_id == user_id, users.c.Is_pay_null == 1)
        re = self.session.execute(s)
        result = re.fetchone()
        return result

    def SELECT_COUNT_REF(self, user_id):
        """
        Получаем количество рефералов пользователя
        :return: int
        """
        s = select(users).where(users.c.Ref == user_id)
        re = self.session.execute(s)
        result_obj = re.fetchall()
        ref_list = []
        for row in result_obj:
            ref_list.append(row._t[1])
        return len(ref_list)

    def SELECT_ID_BLOCK(self, user_id):
        """
        Проверяем удален пользователь или нет
        :param user_id: int
        :return: row | None
        """
        s = select(users).where(users.c.User_id == user_id, users.c.Is_delete == 1)
        re = self.session.execute(s)
        result = re.fetchone()
        return result

    def UPDATE_BLOK(self, user_id, is_blok):
        """
        Назначаем и снимаем БЛОК в отношении пользователя
        :param user_id: int
        :param is_blok: bool
        """
        s = update(users).where(users.c.User_id == user_id).values(Is_delete=is_blok)
        self.session.execute(s)
        self.session.commit()

    def UPDATE_PAYNULL(self, user_id):
        """
        Назначаем и снимаем БЛОК в отношении пользователя
        :param user_id: int
        """
        s = update(users).where(users.c.User_id == user_id).values(Is_pay_null=True)
        self.session.execute(s)
        self.session.commit()


if __name__ == '__main__':
    s = SQL()
    user_id = 725455605
    ref = '725455605'
    is_delete = False
    is_user = s.SELECT_ID(user_id)
    if is_user is None:
        s.INSERT(user_id, True)
    #
    # s.UPDATE_BLOK(3555, 1)
    # if s.SELECT_ID_BLOCK(3555) is not None:
    #     x = s.SELECT_ID_BLOCK(3555)._t
    #     print(f'Пользователь {x[2]} заблокирован')
    # else:
    #     print('Пользователь не заблокирован')
    print(s.SELECT_COUNT_REF(user_id))