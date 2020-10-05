import csv
import getpass
import sys


import requests

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

def print_get_contest(email, password):

    contestsr = requests.get(
        "https://www.hackerrank.com/rest/administration/contests",
        params={
            "offset": 0,
            "limit": 40
        }, auth=(email, password), headers=headers)
    
    if contestsr.status_code != 200:
        print("Error getting contests. Exiting...")
        sys.exit(-1)

    contests_dict = contestsr.json()

    if not contests_dict['status']:
        print("No success getting contests. Exiting...")
        sys.exit(-1)

    contests_list = contests_dict['models']

    for i in range(len(contests_list)):
        print("%d) %s (%s)" %
              (i+1, contests_list[i]['name'], contests_list[i]['slug']))

    c_no = int(input("Enter contest no :"))

    if c_no-1 >= len(contests_list):
        print("Invalid contest no. Exiting...")
        sys.exit(-1)

    return contests_list[c_no-1]['slug'], contests_list[c_no-1]['id']


def get_leaderboard_data(email, password, slug):
    lbr = requests.get(
        "https://www.hackerrank.com/rest/contests/" + slug + "/leaderboard",
        params={
            "offset":0,
            "limit": 500
        }, auth=(email, password), headers=headers)
    
    if lbr.status_code != 200:
        print("Error getting leaderboard. Exiting...")
        sys.exit(-1)
    
    lb_list = lbr.json()['models']
    return lb_list


def get_contest_details(email, password, slug, id):
    time_detailsr = requests.get(
        "https://www.hackerrank.com/rest/administration/contests/" + str(id),
        auth=(email, password), headers=headers)

    if time_detailsr.status_code != 200:
        print("Error getting contest time details. Exiting...")
        sys.exit(-1)

    time_dict_json = time_detailsr.json()

    if not time_dict_json['status']:
        print("Failure while getting contest time details. Exiting...")
        sys.exit(-1)

    time_dict = time_dict_json['model']

    total_time = time_dict['endtime'] - time_dict['starttime']

    score_detailsr = requests.get(
        "https://www.hackerrank.com/rest/administration/contests/"
        + str(id) + "/challenges",
        params={
            "offset": 0,
            "limit": 200
        }, auth=(email, password), headers=headers)

    if score_detailsr.status_code != 200:
        print("Error getting contest score details. Exiting...")
        sys.exit(-1)

    score_dict_json = score_detailsr.json()

    if not score_dict_json['status']:
        print("Failure while getting contest score details. Exiting...")
        sys.exit(-1)

    challenges_list = score_dict_json['models']

    scores = []

    for c in challenges_list:
        scores.append(c['weight'])

    return total_time, scores


def get_leaderboard_file(email, password):
    con_slug, con_id = print_get_contest(email, password)
    ttime, scores = get_contest_details(email, password, con_slug, con_id)
    leaderboard_data = get_leaderboard_data(email, password, con_slug)
    total_score = sum(scores)
    with open('leaderboard-' + con_slug + ".csv", 'w') as lbf:
        fieldnames = ['rank', 'username', 'score', 'normalized_score',
                      'time_in_sec', 'normailzed_time']
        writer = csv.DictWriter(lbf, fieldnames=fieldnames)
        writer.writeheader()

        for lb_entry in leaderboard_data:

            # 100 points
            norm_score = lb_entry['score']/total_score*100
            # 1 hour
            norm_time = lb_entry['time_taken']/(ttime*len(scores))*3600

            writer.writerow({
                'rank': lb_entry['rank'],
                'score': lb_entry['score'],
                'normalized_score': norm_score,
                'time_in_sec': int(lb_entry['time_taken']),
                'normailzed_time': norm_time,
                'username': lb_entry['hacker']
            })

    return True


def main():
  email = input("Enter email :")
  password = getpass.getpass("Enter password (hidden) :")
  
  if get_leaderboard_file(email, password):
    print("Done")


if __name__ == '__main__':
    main()
