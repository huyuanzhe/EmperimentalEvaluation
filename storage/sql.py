
#
HOST = ''
USER_NAME = ''
PASSWD = ''
DATABASES = ''


ONE_YEAR = '2017-09-01'
HALF_YEAR = '2018-03-01'
THREE_MONTH = '2018-06-01'
ONE_MONTH = '2018-08-01'


START_TIME = '2018-09-01'
END_TIME = '2019-09-01'

GET_START_TRAIN_PULL_NUMBER = "select number from pull_request where project='{}' and request_date >'{}' order by number limit 1"
GET_REVIEWER_SQL = "select pull_number,comment_user from comments where project='{}' and pull_number > %d order by pull_number"
# GET_REVIEW_LIST_SQL = "select number from pull_request where project ='robbyrussell/oh-my-zsh' limit 50"
GET_FILE_NAME_SQL = "select pull_number,file_name from request_file where project='{}' and pull_number > %d order by pull_number"

GET_FILE_NAME_BY_PULL_NUMER_SQL = "select distinct pull_number,file_name from request_file where project='{}'"
GET_REVIEWER_BY_NUMBER = "select distinct pull_number,comment_user from comments where project='{}' order by pull_number,comment_date"

GET_TEST_PULL_NUMBER_SQL = "select number from pull_request where project='{}' order by number desc limit %d"
GET_TEST_PULL_NUMBER_SQL2 = "select number from pull_request where request_date between '{}' and '{}' and project='{}' order by request_date"
GET_PULL_REQUEST_TOTAL = "select count(1) from pull_request where project='{}'"
GET_PULL_REQUEST_TOTAL2 = "select count(1) from pull_request where project='{}' and request_date between '2017-09-01' and '2019-09-01'"

GET_PULL_REQUEST_INFO = "select number,title,description from pull_request where project='{}' and request_date > '{}' order by number"
GET_PULL_REQUEST_INFO_BY_TIME = "select number,title,description from pull_request where project='{}' and request_date order by number"
GET_COMMENTS_COUNT_BY_PULL_NUMBER = "select  pull_number,count(1) from comments where project='{}' group by pull_number order by pull_number"

GET_COMMENT_USER_AND_DATE_GROUP_BY_NUMBER = "select pull_number,GROUP_CONCAT(comment_user),GROUP_CONCAT(date_format(comment_date,'%Y-%m-%d')) from comments where project='{}' group by pull_number order by pull_number"
# MySQL DateFormat 函数中 %i 为小时（0-23） %s 为秒（00-59）
GET_COMMENT_USER_AND_DATE_GROUP_BY_NUMBER2 = "select pull_number,GROUP_CONCAT(comment_user),GROUP_CONCAT(date_format(comment_date,'%Y-%m-%d %H:%i:%s')) from comments where project='{}' group by pull_number order by pull_number"

GET_PULL_REQUEST_USER = "select number,user_login from pull_request where project='{}' and request_date between '{}' and '{}' order by number"
GET_PULL_REQUEST_USER2 = "select number,user_login from pull_request where project='{}' and request_date between '{}' and '{}' order by number"

GET_MAX_MIN_COMMENT_DATE = "select max(date_format(comment_date,'%Y-%m-%d')) as max,min(date_format(comment_date,'%Y-%m-%d')) as min from comments where project='{}'"
GET_COMMENT_TIMES = "select comment_user,count(1) as num from comments where project ='{}' group by comment_user order by num desc"

GET_PULL_REQUEST_COUNT = "select count(1) from pull_request where project='{}' and request_date between '{}' and '{}'"

SET_PROJECT_NAME = "set @project='{}'"
GET_PULL_REQUEST_FILE_COUNT = "select pull_number,count(distinct file_name) as num from request_file where project=@project and pull_number in (select number from pull_request where project=@project and request_date between '2010-06-01 00:00:00' and '2019-09-01 00:00:00') group by pull_number order by pull_number"
GET_COMMENT_USER_BY_NUMBER = "select pull_number,GROUP_CONCAT(distinct comment_user) from comments where project=@project and pull_number in (select number from pull_request where project=@project and request_date between '2010-06-01 00:00:00' and '2019-09-01 00:00:00') group by pull_number order by pull_number"
GET_TIME_AFTER_OPEN = "select c.pull_number,timestampdiff(hour,p.request_date,c.comment_date) from (select * from pull_request where project=@project and request_date between '2010-06-01' and '2019-09-01') p inner join (select * from comments where project=@project) c  on c.pull_number=p.number group by c.pull_number order by c.pull_number"
GET_REQUEST_MODULE = "select pull_number,group_concat(distinct substring_index(file_name,'/',2)) from request_file where project=@project and pull_number in (select number from pull_request where project=@project and request_date between '2010-06-01' and '2019-09-01') and locate('/',file_name)>0 group by pull_number"

GET_PROJECT_NAME = 'select project_name from git_project'

GET_REVIEWER_AND_REQUEST = "select comment_user as reviewer,user_login as requester  from (select number,user_login from pull_request where project=@project) p inner join (select comment_user,comment_date,pull_number from comments where project=@project) c on p.number=c.pull_number order by reviewer limit 100"

COUNT_FIRST_COMMENT_DIFF = "select count(1) from (select c.pull_number,timestampdiff(minute,p.request_date,c.comment_date)  as diff from (select * from pull_request where project=@project @project and request_date between '2017-01-01' and '2019-01-01') p inner join (select * from comments where project=@project) c  on c.pull_number=p.number group by c.pull_number having diff<='{}' order by c.pull_number) r"

GET_PULL_REQUEST_USER_AND_DATE = "select number,user_login as requester,CAST(request_date AS CHAR) as request_date from pull_request where project='{}' and request_date <'2019-09-01' order by number"
