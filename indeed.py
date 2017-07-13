import urllib
import urllib2
from bs4 import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup
import urlparse
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import Cookie
# import Queue
import threading
import signal
import time
import sys
import xlwt

from tuning_queries import tuning_queries 
#http://api.indeed.com/ads/apigetjobs?publisher=6265819488525287&jobkeys=2c47f127a8f40d01&v=2

# https://www.indeed.com/rc/clk?jk=2c47f127a8f40d01&fccid=daa11e28e25b811c


# http_proxy  = "http://127.0.0.1:8080"
# https_proxy = "https://127.0.0.1:8080"
# proxyDict = { 
#               "http"  : http_proxy, 
#               "https" : https_proxy 
#             }

 

def print_excel( job_details):  

  # initailize a spreadsheet
  book = xlwt.Workbook(encoding="utf-8")
  sheet  = book.add_sheet("Sheet 1" )

  # write columns headers
  sheet_headers =[ 'job title', 'snippet', 'date', 'company', 'city', 'state', 'formatted Location Full', 'sponsored', 'url', 'job key' ]

  # sheet.col(1).width = 20 * 20

  for header_indx, header in enumerate(sheet_headers):
    # for header_col, header_item in enumerate( header):
          # try:
        # cell width
      #   header_item_length = len(header_item) 
      #   if header_item_length < 50:
      #     sheet.col(header_col).width = ( header_item_length + 6) * 250
      #   else:
      #     sheet.col(header_col).width = 30 * 250
      # except:
        # pass
        
    sheet.write(0 , header_indx,  header  , xlwt.easyxf("align: horiz center "  ))


  for row, jobb in enumerate(job_details):
      for col, item in enumerate( jobb):
          try:
                # cell width
                item_length = len(item) 
                if item_length < 50:
                  sheet.col(col).width = ( item_length + 13) * 250
                elif item_length < 15:
                  sheet.col(col).width = 25 * 250
                else:
                  sheet.col(col).width = 30 * 250

          except:
                  sheet.col(col).width = 15* 250
                  pass

          # write item
          row = row +1
          sheet.write(row , col,  item   , xlwt.easyxf("align: horiz left"  ))
          row= row -1
        
  sheet.col(2).width = 30 * 250
  sheet.col(3).width = 22 * 250
  sheet.col(4).width = 18 * 250
  sheet.col(5).width = 6 * 250
  sheet.col(7).width = 5 * 250

  book.save("aaa.xls")
  sys.exit(0)



def get_cookie():
  try:
    query = 'https://www.indeed.com/jobs?q=marketing&l=New+York,+NY&radius=100&jt=contract&start=980'
    s = requests.Session()
    r = s.get(query, headers ={'Accept': 'text/html,application','Connection': 'close'}  ,verify=False )  
    cookie = r.headers.get('Set-Cookie')
    return cookie 
  except Exception as e:
    if 'HTTPSConnectionPool' in str(e):
      print '[-]check your internet connection'
    return False


def parse_cookie(cookie_value, attripute):
  if cookie_value == False:
    print '[-]there\'s problems parsing the cookie' 
    return False

  cookie = Cookie.SimpleCookie()
  cookie.load(cookie_value)
  parsed = cookie[attripute].value
  return parsed

#cookie to defeat anti-crawling 
raw_cookie = get_cookie()
parsed_cookie = [parse_cookie(raw_cookie,'CTK'),parse_cookie(raw_cookie,'ctkgen'),parse_cookie(raw_cookie,'JSESSIONID'),parse_cookie(raw_cookie,'INDEED_CSRF_TOKEN'),parse_cookie(raw_cookie,'BIGipServerjob_iad')]
cookie ='CTK=1b7ojajfa5ou4f7e'+"; ctkgen="+parsed_cookie[1]+'; JSESSIONID='+parsed_cookie[2]+'; INDEED_CSRF_TOKEN='+parsed_cookie[3]+'; BIGipServerjob_iad='+parsed_cookie[4]




def get_jobkeys(query, start_number, cookie ):
  job_keys = []

  url = str(query)+'&start='+str(start_number)
  s = requests.Session()
  r = s.get(url, headers ={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Cookie': cookie ,'Connection': 'close'}  ,verify=False )#,proxies=proxyDict ) 

  b_soap = BeautifulSoup(r.text, 'html.parser')

  # job_key search term
    # itemprop="title"
  counter = len(b_soap.find_all('a')) 
  for i in range(counter):
    try:
      all_a_tags = b_soap.find_all('a')[i]
      if 'itemprop="title"' in str(all_a_tags):
        job_keys_urls = all_a_tags['href']
        # debug
        # #print job_keys_urls
        parsed = urlparse.urlparse(job_keys_urls)
        parsed_job_key = urlparse.parse_qs(parsed.query)['jk']
        
        if (parsed_job_key in job_keys):
          pass
        else:
          job_keys.append(parsed_job_key[0])
          #debug
          # #print parsed_job_key[0]
    except Exception as e:
      # print '\n\n\n\n\n\n\nerror line 43 '
      # print str(e)
      # print '\n\n\n\n\n\n\n'

      i =- 1
      pass
  ## last page search term = 'rel="next"'

  # if ('rel="next"' not in r.text):
  #   print '\n\n\n\n', url
  #   print 'last page\n\n\n\n\n'
  
  return job_keys




# job details:
def get_job_details(job_key): 
  try:
    url = 'http://api.indeed.com/ads/apigetjobs?publisher=6265819488525287&jobkeys=' + str(job_key) + '&format=json&v=2'
    s = requests.Session()
    r = s.get(url, headers ={'Accept': 'text/html,application','Connection': 'close'}  ,verify=False )  
    #debug
    # #print r.json()
    return r.json()
  except:
    pass

def parse_job_details(job_json_details ):
  try:

    job_title = job_json_details['results'][0]['jobtitle']
    snippet = job_json_details['results'][0]['snippet']
    date = job_json_details['results'][0]['date']
    url = job_json_details['results'][0]['url']
    company = job_json_details['results'][0]['company']
    city = job_json_details['results'][0]['city']
    state = job_json_details['results'][0]['state']
    expired = job_json_details['results'][0]['expired']
    # formattedLocation = job_json_details['results'][0]['formattedLocation']
    formattedLocationFull = job_json_details['results'][0]['formattedLocationFull']
    # formattedRelativeTime = job_json_details['results'][0]['formattedRelativeTime']
    if(job_json_details['results'][0]['sponsored']):
      sponsored = 'sponsored'
    else:
      sponsored = 'no'
     
    jobkey = job_json_details['results'][0]['jobkey']

    details = [ job_title, snippet, date, str(company), city, state, formattedLocationFull, sponsored, url,  jobkey ]
    return details



  except:
    return False




def read_url_list():
  with open('urllist.txt') as f:
    content = f.readlines()
    content = [x.strip() for x in content]
    return content

def write_output(output ,filename):
  f = open( str(filename)+".txt" ,"a" )
  f.write(unicode(output))
  f.close()

def jobs_total_num(jobkeys):
  jobs_total_num =0
  for ndx, jk in enumerate(jobkeys):
    for jkndx, m in enumerate (jk) :
      jobs_total_num += 1
  return jobs_total_num

def check_status(jobkeys):
  while 1:
    time.sleep(10)
    print '\npages total-number for 1 query out of 50 : ',len(jobkeys)      
    print 'jobs total number: ',jobs_total_num(jobkeys)

def limit_jobs(jobkeys, jobs_limit):
  total_num = jobs_total_num(jobkeys)

  if (total_num >= (jobs_limit+60) ) :
    print 'limit reached ', (total_num-60)
    return 'True'
  else:
    return False





def check_integrity():
  query = 'https://www.indeed.com/jobs?q=marketing&l=New+York,+NY&radius=100&jt=contract&start=500'
  job_details = []
  for i in range(2):
    jobkeys = get_jobkeys(query, 70, cookie) 
    job_json_dsc = get_job_details( jobkeys[0] )
    job_dsc = parse_job_details(job_json_dsc)     
    job_details.append(job_dsc)

  #print 'if you see on this url ',query, '  that ', parse_job_details(job_json_dsc)[0], '  ,then the crawler still gives accurat data '
  print job_details
  print_excel(job_details)
  




exit_while = 'False'

class BreakAllTheLoops(BaseException): pass

def main():
  try:

    jobkeys = []
    job_details = []
    query_list = tuning_queries()
    global exit_while   
    # debug for ending
    # query_list = ['https://www.indeed.com/jobs?q=marketing&l=New+York%2CNY&radius=100&jt=part-time&limit=10','https://www.indeed.com/jobs?q=php&l=New+York%2CNY&radius=100&jt=part-time&limit=10']

    print '\nthe results can get up to 51000 jobs ,that will take time'
    jobs_limit_choise = str(raw_input('do you want to limit the total numer of jobs to crawl ? yes or no (prefered): ') )
    if 'yes' in jobs_limit_choise:
      jobs_limit = int(raw_input('\nenter the total number of jobs to crawl (60-51000): '))




    print '\n\n\n        =======================================  CRAWLING INDEED.COM======================================='
    print '\n\n\n[*]queries total number:', len(query_list)

    # status output thread
    t = threading.Thread(target=check_status, args=(jobkeys,))
    t.daemon = True
    t.start()
    

    # loop over all pages
    pages_counter = 0
    while (pages_counter < 1000) & (exit_while == 'False') :
      # debug
      print '\n\n[*]crawling page number ['+ str(pages_counter)+ '] for all queries/locations\n\n\n'

      # try:
      # get the job keys
      if exit_while == 'False':
        for query in query_list:
          keys = get_jobkeys(query, pages_counter, cookie) 

          # for jobs status
          jobkeys.append(keys)

          # get the job details
          for ndx, job in enumerate(keys) : 
            if 'jobs_limit' in locals():
              # check if its exceded
              # print 'checkkkkk'
              is_exceded = limit_jobs(jobkeys, jobs_limit)
              if (is_exceded == 'True'):                  
                raise BreakAllTheLoops()                  
            try:
              job_json_dsc = get_job_details( job)
              job_dsc = parse_job_details(job_json_dsc)     
              # print job_dsc[0]
              if job_dsc != False:
                job_details.append(job_dsc)

            
          # except KeyboardInterrupt:
          #   print("W: interrupt received")
          #   print_excel(job_details)
          #   sys.exit(0) 
            except TypeError:
              pass
          

          
      # increament  "&start=" / pages  by 10
      pages_counter = pages_counter + 10

      # except Exception as e:
      #   print 'error line 152'
      #   print str(e)
      #   if 'HTTPSConnectionPool' in str(e):
      #     print '[-]there\'s problems getting the cookie' 
      #   pass

    #save all job keys as backup 
    # write_output(jobkeys,'jobkeys' )

    

    print_excel(job_details)
  except (BreakAllTheLoops,KeyboardInterrupt):
    print_excel(job_details)
    pass


main()

# check_integrity() 

