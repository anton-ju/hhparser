import argparse
import json

from parsers import hhparser
from storage import hand_storage
import pandas as pd
from xml.dom import minidom
import datetime
import logging
import os.path

config = {
    "HERO": 'DiggErr555',
    "START_DATE": '2018-12-01',
    "END_DATE": str(datetime.date.today()),
    "FISH_LABELS": ('15', '16', '17', '18', 'uu'),
    "NOTES_FILE": 'c:\\Users\\user\\AppData\\Local\\PokerStars\\notes.DiggErr555.xml'
}


def message(msg, error_level):
    """
    if error sys.exit() calls
    :param msg: message to write in log
    :param error_level:
    :return:
    """
    tell = {
        logging.INFO: logging.info,
        logging.ERROR: logging.error
    }
    tell[error_level](msg)
    if error_level >= logging.ERROR:
        raise RuntimeError(msg)


def load_ps_notes(notes_file):
    if not os.path.exists(notes_file):
        raise RuntimeError('Path not exists')
    if not os.path.isfile(notes_file):
        raise RuntimeError('Not a file')

    xml = minidom.parse(notes_file)
    notes = xml.getElementsByTagName('note')
    notes_dict = {}
    for note in notes:
        notes_dict[note.attributes['player'].value] = note.attributes['label'].value

    return notes_dict


def fish_per_table(players_list, notes_dict):
    """
    :param players_list:
    :param notes_dict:
    :return: number of players with FISH_LABELS + unknowns
    """
    count = 0
    for player in players_list:

        if notes_dict.get(player, 'uu') in config['FISH_LABELS']:
            count += 1
    return count


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', action='store', help='Config file', default='roi.cfg')
    return parser.parse_args()


def load_config(config_current, config_file):
    try:
        with open(config_file, 'r') as f:
            config_json = f.read()
            if config_json == '':
                return
            new_config = json.loads(config_json, encoding='utf-8')
            if new_config:
                config_current.update(new_config)
    except IOError:
        message('Error opening config file', logging.ERROR)
    except json.JSONDecodeError:
        message('Invalid config file structure', logging.ERROR)


def main():
    logging.basicConfig(
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S',
        level=logging.INFO
    )

    args = parse_arguments()
    load_config(config, args.config)
    logging.info('Start...')
    notes = load_ps_notes(config['NOTES_FILE'])
    logging.info('Player notes loaded...')
    hero = config['HERO']
    storage = hand_storage.HandStoragePgsql(dbname='nolim 2.3.0 04-12-2017',
                                            user='postgres',
                                            host='127.0.0.1',
                                            port='5318',
                                            pwd='')

    # storage = hand_storage.HandStorage('hands/debug')
    results_icm = {}
    results_bounty = {}
    tournaments = {}
    finishes = {}
    logging.info('Selecting hands...')
    for hand in storage.read_hand(start_date=config['START_DATE'], end_date=config['END_DATE']):
    # for hand in storage.read_hand():
        try:
            hh = hhparser.HHParser(hand)

        except Exception as e:
            logging.info(hh)
            logging.info(e)
            continue
        if hh.hero != hero:
            continue
        if hh.bi not in (10.0, 25.0, 5.0, 100.0, 50.0):
            continue
        if tournaments.get(hh.tid) is None:
            # if len(hh.players) == 6:
            tournaments[hh.tid] = [[hh.bi, hh.datetime, fish_per_table(hh.players, notes), hh.bounty]]
            results_icm[hh.tid] = -hh.bi + hh.prize_won.get(hero, 0)
            results_bounty[hh.tid] = hh.bounty_won.get(hero, 0)
        else:
            tournaments[hh.tid].append([hh.bi, hh.datetime, fish_per_table(hh.players, notes), hh.bounty])
            results_icm[hh.tid] += hh.prize_won.get(hero, 0)
            results_bounty[hh.tid] += hh.bounty_won.get(hero, 0)

        if hh.finishes.get(hero):
            finishes[hh.tid] = hh.finishes.get(hero)

        # logging.info(f'{results_bounty[hh.tid]} {hh.hid} {hh.datetime}')

    logging.info('Calculating statistics')
    results = []
    for tour, value in tournaments.items():
        if finishes.get(tour) is None:
            ts_text = storage.read_summary(tour)
            if ts_text:
                ts = hhparser.TournamentSummary(ts_text)
                finishes[tour] = ts.finishes
                results_icm[tour] += ts.prize_won.get(hero, 0)
                if ts.finishes == 1:
                    logging.info(results_bounty[tour])
                    results_bounty[tour] += value[0][3] * 2

        results.append([tour,
                        value[0][0],
                        min([_[1] for _ in value]),
                        max([_[2] for _ in value]),
                        results_icm[tour],
                        results_bounty[tour],
                        results_icm[tour] + results_bounty[tour],
                        finishes.get(tour, 0),
                        len(value)
                       ])

    if results:
        logging.info('Saving results...')
        df = pd.DataFrame(results)
        columns = ['tid', 'bi', 'date', 'fish', 'prize_won', 'bounty_won', 'total_won', 'finishes', 'hands']
        df.to_csv(f'results {config["START_DATE"]} {config["END_DATE"]}.csv', header=columns)
        logging.info('Success')
    else:
        logging.info('No tournament results found!')

if __name__ == '__main__':
    main()
