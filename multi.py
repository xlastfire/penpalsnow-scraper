import requests
from bs4 import BeautifulSoup
from time import sleep
from random import randint
from datetime import datetime
from config import target, gender, age_group, country, need_output
from values import COUNTRIES, AGES, GENDERS
import re

url = 'https://www.penpalsnow.com/do/search.html'


def validate_inputs(target_input, gender_input, age_group_input, country_input, need_output_input):
    try:
        if target_input < 0:
            print('Enter positive value for target.')
            return False
        if target_input > 50:
            print("Enter below 50 for not to be blocked.")
            return False
    except:
        print('Enter valid value.')
        return False

    if gender_input not in GENDERS and gender_input != '':
        print('Gender is not valid.')
        return False

    if age_group_input not in AGES and age_group_input != '':
        print('Age-Group is not valid.')
        return False

    if country_input.lower() not in COUNTRIES and country_input != '':
        print('Country is not valid.')
        return False

    if need_output_input.lower() != 'true' and need_output_input.lower() != 'false':
        print('Need-Output is not valid. First character should be CAPITAL LETTER')
        return False

    return True


def getIDs(text):
    ids = []
    for word in text:
        if 'id="' in word:
            ids.append(word.split('"')[1])
    return ids


def deEmojify(text):
    regrex_pattern = re.compile(pattern="["
                                        u"\U0001F600-\U0001F64F"  # emoticons
                                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                        "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)


def multipages(target=10, found=0, session=None, gender='female', age_group='19-22', country='UK', num=0, output=None):
    if session is None:
        with requests.Session() as session:
            login_data = {
                'sex': gender,
                'agegroup': age_group,
                'hobbies': '',
                'country': country,
                'city': '',
                'language': '',
                'search': 'Find+penpals!%21',
                'numb': num,
                'search': 'Find+penpals!%21'
            }

            r = session.get(url)

            r = session.post(url, data=login_data)

    else:
        login_data = {
            'transfer': gender + '||X||' + age_group + '||X||' + country + '||X||||X||||X||||X||||X||',
            'numb': num,
            'search': 'Next 5 pen pal ads'
        }
        r = session.post(url, data=login_data)

    soup = BeautifulSoup(r.content, 'html5lib')

    uu = 'https://www.penpalsnow.com/_api/showemail.php?e='

    ids = getIDs(r.text.split(" "))

    paragraphs = soup.find_all('p')

    paras = []
    for para in paragraphs:
        paras.append(para)

    index = 0

    for i in range(2, len(paras)):
        vals = paras[i].find_all('span', class_='ppadvaluebold')
        if len(vals) != 3:
            continue
        # print(paras[i])
        name = str(vals[0].text).strip()
        gender = str(vals[1].text).strip()
        age = str(vals[2].text).strip()
        address = str(paras[i].find('address').find('span', class_='ppadvalue').text).strip().replace("\n",
                                                                                                      ',').replace(
            '       ', ' ')
        email = requests.get(uu + ids[index]).text

        para = str(paras[i].find('span', class_='ppadvaluemsg').text).strip().replace("\n\n", '\n')
        date = str(paras[i].find('span', class_='ppaddatevalue').text).strip()
        date1 = date[:4] + '/' + date[4:6] + '/' + date[6:]

        result = f'Name - {name} Age - {age} Gender - {gender} Email - {email}\n Address - {address} Last Modified - {date1} \n Msg - {para}\n'
        result += '---------------------------------------------------------------------------------'

        if output is not None:
            try:
                output.write(result+'\n')
            except UnicodeEncodeError:
                print('Emoji found. So removing it.', end=' ')
                output.write(deEmojify(result)+ '\n')
            except:
                print('Any other error while writing to a text file. So Skipping')
                continue

        else:
            print(result)

        print(f'{found + 1} Scraped!')
        found += 1
        index += 1

    if found >= target:
        return
    else:
        interval = randint(2, 5)
        print(f'\n>> Waiting - {interval}s for next <<')
        sleep(interval)
        num += 5
        multipages(target, found, session, gender, age_group, country, num, output)


if __name__ == '__main__':

    target = target
    gender = gender
    age_group = age_group
    country = country.lower()
    need_output = need_output

    not_error = True
    if not validate_inputs(target, gender, age_group, country, need_output):
        print('Existing', end='')
        for i in range(4):
            sleep(1)
            print('.', end='')
        not_error = False

    if not_error:
        if need_output.lower() == 'true':
            now = datetime.now()
            name = now.strftime("%Y.%m.%d,%H.%M.%S" + ".txt")
            output = open(name, 'w')
        else:
            output = None

        multipages(target, found=0, gender=gender, age_group=age_group, country=COUNTRIES[country.lower()], num=0, output=output)

        if output is not None:
            output.close()
