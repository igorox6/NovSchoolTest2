import discord
from discord.ext import commands
import config

import pymysql
import random



def getNameSurname(login:str,pwd:str):
    try:
        # cursor.execute("Команда") # При создании таблицы / получении данных
        # cursor.commit("Команда") # При вставке данных
        connection = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                command = f"SELECT concat(Name,' ',SecondName) as Name from users join student on users.idUser=student.idUser where Login ='{login}' and Password='{pwd}'"
                cursor.execute(command)
                rows = cursor.fetchall()

                if rows:
                    name = rows[0]['Name']
                    return name
                else:
                    command = f"SELECT concat(Name,' ',SecondName) as Name from users join worker on users.idUser=worker.idUser where Login ='{login}' and Password='{pwd}'"
                    cursor.execute(command)
                    rows_1 = cursor.fetchall()
                    if rows_1:
                        name = rows_1[0]['Name']
                        return name
                    else:
                        return None
        finally:
            connection.close()

    except Exception as ex:
        print(f"Ошибка: {ex}")


def giveRole(login:str):
    try:
        connection = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                command = f"SELECT concat(ClassNumber,ClassLetter) as class from users join student on users.idUser=student.idUser join class on student.idClass=class.idClass where Login ='{login}'"
                cursor.execute(command)
                rows = cursor.fetchall()

                if rows:
                    match (rows[0]['class']):
                        case "4А":
                            roles=["1261704771400765450"]
                        case "4Б":
                            roles = ["1261705530649346198"]
                        case "5А":
                            roles = ["1261705267540660296"]



                    roles.append("1261703915507023963") # Вторая роль-ученик

                else:
                    roles=["1261706145874313296"] # Роль-учитель
                return roles

        finally:
            connection.close()

    except Exception as ex:
        print(f"Ошибка: {ex}")


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Задаём префикс и интенты
bot = commands.Bot(command_prefix='/', intents=intents)
user_emails = {}
tryGuessNumber = {}

"""@bot.event
async def on_message(ctx):
    if ctx.author != bot.user:
        if ctx.content == "Привет!":
            await ctx.reply(ctx.content)"""



@bot.command()
async def commands(ctx):
    await ctx.reply("Привет! Я нужен для того, чтобы помогать вам учиться и отдыхать!\n"
                    "Список моих команд:\n"
                    "/login <Ваш логин> <Ваш пароль>\n"
                    "/random_number Нужно угадать число от 0 до 10\n")

"""
@bot.command()
async def deleteMsg(ctx):
    await ctx.message.delete() # Удаление
    await ctx.author.send("Ваше сообщение было удалено") #Лс
"""

@bot.command()
async def ping(ctx):
    """
    <@idUser>
    <#idChannel>
    <@&idRole>
    """
    await ctx.send('123')
    if ctx.author != bot.user:
        await ctx.send(ctx.author.display_name)

@bot.command()
async def randomNumber(ctx,precision: int = None):
    if precision!=None:
        random_number: int = random.randint(1, 10)

        user_id = ctx.author.id
        if user_id not in tryGuessNumber:
            tryGuessNumber[user_id] = 0

        if precision == random_number:
            attempts = tryGuessNumber[user_id]
            await ctx.reply(f"Поздравляю! Вы угадали! Ваше количество попыток: {attempts}.")
            tryGuessNumber[user_id] = 0  # Обнуляем счетчик
        else:
            tryGuessNumber[user_id] += 1
            await ctx.reply(
                f"К сожалению, вы не угадали... Загаданным числом являлось {random_number}.")




@bot.command()
async def login(ctx, *args):
    if (len(args) !=2):
        await ctx.author.send('Авторизация на сервере не была проивзедена(Введено неверное количество аргументов).'
                              '\nПожалуйста, напишите в чат "Авторизация" команду /login <Ваш логин> <Ваш пароль>')
        return

    bot_member = ctx.guild.me
    author_member = ctx.author

    if author_member.top_role >= bot_member.top_role:
        await ctx.send('Я не могу изменить ваш никнейм, так как у вас более высокая роль или вы администратор.')
        return

    resultLogin=getNameSurname(args[0],args[1])
    if (resultLogin==None):
        await ctx.author.send('Авторизация на сервере не была проивзедена.\nПожалуйста, напишите в чат "Авторизация" команду /login <Ваш логин> <Ваш пароль>')

    else:
        try:
            await author_member.edit(nick=resultLogin)

            roles = (giveRole(args[0]))
            for i in roles:
                role = ctx.guild.get_role(int(i))
                await author_member.add_roles(role)

            await ctx.author.send((f'Авторизация в Дискорде Онлайн школы №36 под логином {args[0]} произошла успешно.'))
            await ctx.message.delete()
        except discord.Forbidden:
            await ctx.send('Отсутствует разрешение на изменение никнейма.')
            await ctx.message.delete()
        except discord.HTTPException as e:
            await ctx.send(f'Произошла ошибка при изменении никнейма: {e}')
            await ctx.message.delete()



@bot.command()
async def loginSpecialUser(ctx, member: discord.Member, *, new_nickname: str = None):
    if str(ctx.author.top_role) == "Администратор":

        if new_nickname is None:
            await ctx.send('Вы не указали новый никнейм.')
            return

        bot_member = ctx.guild.me
        if member.top_role >= bot_member.top_role:
            await ctx.send(
                'Я не могу изменить никнейм этого пользователя, так как у него более высокая роль или он администратор.')
            return

        try:
            await member.edit(nick=new_nickname)
            await ctx.send(f'Никнейм пользователя был изменен на {new_nickname}')
        except discord.Forbidden:
            await ctx.send('Отсутствует разрешение на изменение никнейма.')
        except discord.HTTPException as e:
            await ctx.send(f'Произошла ошибка при изменении никнейма: {e}')


bot.run(config.TOKEN)
