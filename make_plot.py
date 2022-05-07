from sqlalchemy import text
import pandas as pd
from time import localtime, time
import matplotlib.pyplot as plt
import datetime
import matplotlib.font_manager as fm
font = fm.FontProperties(fname='DoHyeon-Regular.ttf')
import matplotlib
matplotlib.use('agg')

tm = localtime(time())
time_now = tm.tm_hour*60 + tm.tm_min

def query_table(db):
    query = '''
            select
                member_id,
                Date(create_time),
                post_times.times
            from
                post
            inner join post_times
                        on
                post.post_id = post_times.post_post_id
            where
                date_sub(now(), interval 7 day) < post.create_time AND post.create_time < now()
            '''
    result = db.execute(query)
    query_member = text('select member_id, name from member')
    member_name = db.execute(query_member)
    return [*result], [*member_name]

def change_time(string):
    global time_now
    t = string.split(',')
    total, prev = 0,-1
    for i, s in enumerate(t):
        tmp = s.split(":")
        v = int(tmp[0])*60 +int(tmp[1])
        if i%2 ==0:
            prev = v
        else:
            if prev > v:
                v+= 60*24
            total += (v-prev)
            prev = -1

    return total/60

def make_dataframe(result, member_name):
    members = [None]+[*map(lambda x : x[1], member_name)]
    result = pd.DataFrame(result)
    table = pd.DataFrame(result.groupby(['member_id','Date(create_time)'])['times'].apply(','.join)).reset_index()
    table['times'] = table['times'].apply(change_time)
    table['member_id'] = table['member_id'].apply(lambda x : members[x])
    table.columns = ['작성자', 'date', '학습시간']
    return table

def make_plot(result, member_name):
    data = make_dataframe(result, member_name)
    data['date'] = pd.to_datetime(data['date'])

    # 미공부시간 만들기
    arr_tmp = []
    for name in data['작성자'].unique():
        for i in range(1, 8):
            tmp = datetime.date.today() - datetime.timedelta(days=i)
            tmp_day =pd.to_datetime(tmp)
            if len(data[(data['작성자'] == name) & (data['date'] == tmp_day)]) < 1:
                arr_tmp.append([name, tmp_day, 0])
    tmp_pd = pd.DataFrame(arr_tmp)
    tmp_pd.columns = ['작성자', 'date', '학습시간']
    data = pd.concat([data, tmp_pd],ignore_index=True)
    
    colors = ['#79C1E6','#429981','#DD9CE6','#FFB207'] * len(data['작성자'].unique())

    fig, ax = plt.subplots(figsize=(30,15))
    xticks_date = data[data['작성자'] == data['작성자'][0]]['date']
    weekday = ['월', '화', '수', '목', '금', '토', '일']
    weekdays1 = [*map(lambda x : str(x)[5:10] + "(" + weekday[x.date().weekday()] + ")" , xticks_date)]
    weekdays1 = [*map(lambda x : x.replace("-", "/"), weekdays1)]
    weeks_study_time = []

    for user, color in zip(data['작성자'].unique(),colors):
        data_user = data[data['작성자'] == user].sort_values(by='date')
        data_user['학습시간'] = data_user['학습시간'].cumsum()
        plt.plot(data_user['date'].values , data_user['학습시간'].values, lw=6, color=color)
        plt.scatter(data_user['date'].values , data_user['학습시간'].values, s=150, color=color)

        time = data_user.tail(1)['학습시간'].values[0]
        date = data_user.tail(1)['date'].values[0] + pd.to_timedelta('6 hours')
        weeks_study_time.append([user, round(time,2), date, color, time])

    weeks_study_time = sorted(weeks_study_time, key=lambda x: x[1], reverse=True)
    for i in range(1, len(weeks_study_time)):
        if weeks_study_time[i][1] > weeks_study_time[i-1][1] - 4:
            weeks_study_time[i][4] = weeks_study_time[i-1][4] - 4

    for user, time, date, color, y_position in weeks_study_time:
        plt.text(s=f'{user}', x=date, y = y_position,font=font, fontsize=30, va='center', ha='center', color=color)
        plt.text(s=f'{round(time,2)}시간', x=date, y=y_position-1.7,font=font, fontsize=20, va='center', ha='center', color=color)

    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['top'].set_visible(False)
    plt.grid()

    first, end = "Now", str(data.tail(1)['date'].values)[7:12]
    end = end.replace('-', '/')
    plt.title(f'일주일간 공부시간 ({end} ~ {first})', font=font, fontsize= 40,pad=32)

    plt.ylabel('공부시간 (누적)',font=font, fontsize=30)
    plt.xlabel('',font=font, fontsize=30)
    plt.xticks([], font=font, fontsize=40)
    plt.yticks(font=font,fontsize=40)

    for i, v in enumerate(xticks_date):
        plt.text(s=weekdays1[i], x= v, y=-0.5,font=font, fontsize=40, va='top', ha='center')
        plt.axvline(v, color='gray', alpha = 0.5)
    plt.ylim(0, )

    fig.savefig('my_plot.png')