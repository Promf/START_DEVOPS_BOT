import os
from dotenv import load_dotenv
import logging
import re
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import paramiko
import psycopg2
from psycopg2 import Error

load_dotenv()
TOKEN = os.getenv('TOKEN')

logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)



def sql_select_emails(query):
    s = ''
    try:
        connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                  password=os.getenv("DB_PASSWORD"),
                                  host=os.getenv("DB_HOST"),
                                  port=os.getenv("DB_PORT"),
                                  database=os.getenv("DB_DATABASE"))

        cursor = connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        for row in data:
            s += str(row[0]) + '. ' + row[1]+ '\n'
        logging.log("Команда успешно выполнена")


    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)

    finally:
        if connection is not None:
            cursor.close()
            connection.close()
        return s

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

def helpCommand(update: Update, context):
    update.message.reply_text('Help!')


def execute_command(command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(os.getenv('RM_HOST'), username=os.getenv('RM_USER'), password=os.getenv('RM_PASSWORD'))
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read().decode()
    ssh.close()
    return result

def get_release(update, context):
    command = 'cat /etc/os-release'
    result = execute_command(command)
    send_long_message(update, context, result)

def get_uname(update, context):
    command = 'uname -a'
    result = execute_command(command)
    send_long_message(update, context, result)

def get_uptime(update, context):
    command = 'uptime'
    result = execute_command(command)
    send_long_message(update, context, result)

def get_df(update, context):
    command = 'df -h'
    result = execute_command(command)
    send_long_message(update, context, result)

def get_free(update, context):
    command = 'free -h'
    result = execute_command(command)
    send_long_message(update, context, result)

def get_mpstat(update, context):
    command = 'mpstat'
    result = execute_command(command)
    send_long_message(update, context, result)

def get_w(update, context):
    command = 'w'
    result = execute_command(command)
    send_long_message(update, context, result)

def get_auths(update, context):
    command = 'tail -n 10 /var/log/auth.log'
    result = execute_command(command)
    send_long_message(update, context, result)

def get_critical(update, context):
    command = "grep -i 'crit' /var/log/syslog | tail -n 5"
    result = execute_command(command)
    send_long_message(update, context, result)

def get_ps(update, context):
    command = 'ps aux'
    result = execute_command(command)
    send_long_message(update, context, result)

def get_ss(update, context):
    command = 'ss -tuln'
    result = execute_command(command)
    send_long_message(update, context, result)

def get_emails(update, context):
    send_long_message(update, context, sql_select_emails('SELECT * FROM emails;'))

def get_phone_numbers(update, context):
    send_long_message(update, context, sql_select_emails('SELECT * FROM phone_numbers;'))

MAX_MESSAGE_LENGTH = 4096  # Максимальная длина сообщения в Telegram

def send_long_message(update, context, text):
    if(not text):
        update.message.reply_text('Ничего не найдено')
        return
    for i in range(0, len(text), MAX_MESSAGE_LENGTH):
        update.message.reply_text(text[i:i + MAX_MESSAGE_LENGTH])


def get_apt_list(update, context):
    user_input = update.message.text
    if(user_input=='1'):
        command = 'apt list --installed'
        result = execute_command(command)
        send_long_message(update, context,result)

    else:
        command = 'apt show ' + str(user_input)
        result = execute_command(command)
        send_long_message(update, context, result)
    return ConversationHandler.END

def get_services(update, context):
    command = 'systemctl list-units --type=service --no-pager'
    result = execute_command(command)
    send_long_message(update, context, result)


def echo(update: Update, context):
    update.message.reply_text(update.message.text)
    #update.message.reply_text(execute_command(update.message.text))


def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'findPhoneNumbers'

def findEmailCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска почтовых адресов: ')
    return 'findEmail'

def verifyPasswdCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки: ')
    return 'verifyPasswd'

def get_apt_list_command(update: Update, context):
    update.message.reply_text('1. Вывод всех пакетов(введите 1)\n2. Поиск информации о пакете(введите название пакета): ')
    return 'apt_list_choice'

def get_services_command(update: Update, context):
    update.message.reply_text('Введите команду: ')
    return 'getServices'

def confirmYesHandler(update: Update, context):
    try:
        connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                  password=os.getenv("DB_PASSWORD"),
                                  host=os.getenv("DB_HOST"),
                                  port=os.getenv("DB_PORT"),
                                  database=os.getenv("DB_DATABASE"))

        cursor = connection.cursor()
        phoneNumberList = context.user_data.get('phone_numbers')
        for number in phoneNumberList:
            cursor.execute(f"INSERT INTO phone_numbers (phone) VALUES ('{number}')")
        connection.commit()
        logging.info("Команда успешно выполнена")
        update.message.reply_text('Успешно сохранено.')

    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        update.message.reply_text('Ошибка.')

    finally:
        if connection is not None:
            cursor.close()
            connection.close()

    return ConversationHandler.END

def confirmYesEmail(update: Update, context):
    try:
        connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                  password=os.getenv("DB_PASSWORD"),
                                  host=os.getenv("DB_HOST"),
                                  port=os.getenv("DB_PORT"),
                                  database=os.getenv("DB_DATABASE"))

        cursor = connection.cursor()
        Emails = context.user_data.get('Emails')
        for mail in Emails:
            cursor.execute(f"INSERT INTO emails (email) VALUES ('{mail}')")
        connection.commit()
        logging.info("Команда успешно выполнена")
        update.message.reply_text('Успешно сохранено.')

    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
        update.message.reply_text('Ошибка.')

    finally:
        if connection is not None:
            cursor.close()
            connection.close()

    return ConversationHandler.END

def confirmNoHandler(update: Update, context):
    update.message.reply_text('Данные не будут сохранены.')
    return ConversationHandler.END

def confirmNoEmail(update: Update, context):
    update.message.reply_text('Данные не будут сохранены.')
    return ConversationHandler.END


def verifyPasswd(update: Update, context):
    user_input = update.message.text

    passwordRegex = re.compile(
    r'^(?=.*[A-Z])'      # Проверка на наличие хотя бы одной заглавной буквы
    r'(?=.*[a-z])'       # Проверка на наличие хотя бы одной строчной буквы
    r'(?=.*\d)'          # Проверка на наличие хотя бы одной цифры
    r'(?=.*[!@#$%^&*()])' # Проверка на наличие хотя бы одного специального символа
    r'.{8,}$'            # Проверка на длину пароля: не менее 8 символов
    )
    Passwords = passwordRegex.findall(user_input)

    if not Passwords:
        update.message.reply_text('Пароль лёгкий')
        return # Завершаем выполнение функции

    s = ''
    for i in range(len(Passwords)):
        s += f'Сложный пароль. {Passwords[i]}\n'
    update.message.reply_text(s) # Отправляем сообщение пользователю
    return ConversationHandler.END # Завершаем работу обработчика диалога

def findEmail(update: Update, context):
    user_input = update.message.text

    emailRegex = re.compile(
    r"[a-zA-Z0-9_.+-]+"
    r"@"
    r"[a-zA-Z0-9-]+"
    r"\."
    r"[a-zA-Z0-9-.]+")

    Emails = emailRegex.findall(user_input)

    if not Emails: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Почтовые адреса не найдены')
        return # Завершаем выполнение функции
    context.user_data['Emails'] = Emails
    emailNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(Emails)):
        emailNumbers += f'{i+1}. {Emails[i]}\n' # Записываем очередной номер

    update.message.reply_text(emailNumbers) # Отправляем сообщение пользователю
    update.message.reply_text('Чтобы сохранить в БД, напишите Да, иначе напишите Нет')
    return 'confirmActionEmail'


def findPhoneNumbers (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(
    r'(?:\+?7|8)[\s-]*'
    r'(?:\(?\d{3}\)?)[\s-]*'
    r'\d{3}[\s-]*'
    r'\d{2}[\s-]*'
    r'\d{2}')

    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return
    context.user_data['phone_numbers'] = phoneNumberList
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' # Записываем очередной номер

    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    update.message.reply_text('Чтобы сохранить в БД, напишите Да, иначе напишите Нет')
     # Завершаем работу обработчика диалога
    return 'confirmAction'


def get_repl_logs(update, context):
    command = 'cat /var/lib/postgresql/data/log/*'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(os.getenv('DB_HOST'), username=os.getenv('root'), password=os.getenv('DB_PASSWORD'))
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read().decode()
    ssh.close()
    s = ''
    for line in result.splitlines():
        if 'replication' in line:
            s+= line + "\n"
    send_long_message(update, context, s)

def main():

    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_numbers', findPhoneNumbersCommand)],
        states={
        'findPhoneNumbers': [
            MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)
        ],
        'confirmAction': [
            MessageHandler(Filters.regex('^(Да)$'), confirmYesHandler),
            MessageHandler(Filters.regex('^(Нет)$'), confirmNoHandler),
        ],
    },
        fallbacks=[]
    )

    convHandlerFindEmail = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailCommand)],
        states={
            'findEmail': [MessageHandler(Filters.text & ~Filters.command, findEmail)
            ],
            'confirmActionEmail': [
            MessageHandler(Filters.regex('^(Да)$'), confirmYesEmail),
            MessageHandler(Filters.regex('^(Нет)$'), confirmNoEmail),
        ],

        },
        fallbacks=[]
    )

    convHandlerVerifyPasswd = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswdCommand)],
        states={
            'verifyPasswd': [MessageHandler(Filters.text & ~Filters.command, verifyPasswd)],
        },
        fallbacks=[]
    )

    convHandlerAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list_command)],
        states={
            'apt_list_choice': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )



    dp.add_handler(CommandHandler("start", start))

    dp.add_handler(CommandHandler("help", helpCommand))

    dp.add_handler(CommandHandler("get_release", get_release))

    dp.add_handler(CommandHandler("get_uname", get_uname))

    dp.add_handler(CommandHandler("get_uptime", get_uptime))

    dp.add_handler(CommandHandler("get_df", get_df))

    dp.add_handler(CommandHandler("get_free", get_free))

    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))

    dp.add_handler(CommandHandler("get_w", get_w))

    dp.add_handler(CommandHandler("get_auths", get_auths))

    dp.add_handler(CommandHandler("get_critical", get_critical))

    dp.add_handler(CommandHandler("get_ps", get_ps))

    dp.add_handler(CommandHandler("get_ss", get_ss))

    dp.add_handler(CommandHandler("get_services", get_services))

    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))

    dp.add_handler(CommandHandler("get_emails", get_emails))

    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))



    dp.add_handler(convHandlerFindPhoneNumbers)

    dp.add_handler(convHandlerFindEmail)

    dp.add_handler(convHandlerVerifyPasswd)

    dp.add_handler(convHandlerAptList)

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))



    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
