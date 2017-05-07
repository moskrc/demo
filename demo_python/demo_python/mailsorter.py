import getopt, sys
import poplib, email
import re
import os
import datetime
    
PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
    
class MailSorter(object):
    """ Base func """
    
    def __init__(self, server, user, password):
        """ Constructor """
        
        self.server = server
        self.user = user
        self.password = password
        self.counter = {}

    def inc_counter(self,key):
        if key in self.counter:
            self.counter.update({key:self.counter[key]+1})
        else:
            self.counter[key]=1

    def check_mail(self):
        """ Check mail """
        
        print 'Connecting to pop3 mail server'
        con = poplib.POP3_SSL(self.server)
        con.getwelcome()
        con.user(self.user)
        con.pass_(self.password)
        response, lst, octets = con.list()
        
        print 'Check mail, total found %d letters' % (len(lst))
        
        for msg_num, msgsize in [i.split() for i in lst]:
            (resp, lines, octets) = con.retr(msg_num)
            message = email.message_from_string("\n".join(lines) + "\n\n")
            print 'Download message %d of %d...' % (int(msg_num), len(lst),)
            self.save_message(message)
            con.dele(msg_num)
        
        print "Disconnecting..."
        
        with open(os.path.join(PROJECT_DIR,str(datetime.datetime.today())),'w') as file:
            file.write("Date: %s\n" % (datetime.date.today()))
            file.write("Total mail received: %d\n" % (len(lst)))
            for key in self.counter:
                file.write("Mail received at %s: %d\n" % (key,self.counter[key]))    
        
        con.quit()
        
    def save_message(self, message):
        """ Save message """
        msg_from = message['from']
        msg_to = message['to']
        msg_date = message['date']        
        msg_subject = "".join([text for text, enc in email.Header.decode_header(message['subject'])])
        
        if not msg_subject:
            msg_subject = 'no_subject'
            
        msg_parts = [(part.get_filename(), part.get_payload(decode=True)) for part in message.walk()]

        body = ""

        for name, data in msg_parts:
            if not name and data:
                body = data

        if body:
            try:
                if re.search("<(.*)>",msg_to):
                    msg_to = re.search("<(.*)>",msg_to).groups()[0]
                user, domain = msg_to.split('@')

                self.inc_counter("%s@%s" % (user,domain,))

                                
                domain_path = os.path.join(PROJECT_DIR,domain)
                if not os.path.exists(domain_path):
                    os.mkdir(domain_path)
                
                user_path = os.path.join(domain_path, user)
                if not os.path.exists(user_path):
                    os.mkdir(user_path)

                with open(os.path.join(user_path,msg_subject),'w') as file:
                    file.write("Date: %s\n" % (msg_date))
                    file.write("From: %s\n" % (msg_from))
                    file.write("Message: %s\n" % (body))
            except:
                pass

# ============================================================================

def main():
    """ Loader """

    # Parse command line
    SERVER = ''
    USER = ''
    PASSWORD = ''
   
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dhs:u:p:", ["debug","help","server=","user=","password="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-s", "--server"):
            SERVER = a
        elif o in ("-u", "--user"):
            USER = a
        elif o in ("-p", "--password"):
            PASSWORD = a
        else:
            assert False, "unhandled option"
            
    if not SERVER:
        print "-s | --server option required"
        sys.exit()
        
    if not USER:
        print "-u | --user option required"
        sys.exit()
        
    if not PASSWORD:
        print "-p | --password option required"
        sys.exit()
    
    # Starting MailSorter'a
    print "Starting..."
    mc = MailSorter(SERVER, USER, PASSWORD)
    mc.check_mail()

def usage():
    """ Help """
    print 'Usage: mailcommander.py -s mail_server -u mail_user -p mail_user_password'

if __name__ == "__main__":
    main()

