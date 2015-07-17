#!/usr/bin/python3
#
# snippets1.py: 
#
# @author Francis Kessie
#
"""
A command line note taking application.

You can store snippets of text by keywords, retrieve the messages 
using the keywords or retrieve messages by searching for words contained within 
the messages. It generates a log file to track functionality. 

for usage: python3 snippets1.py -h
"""
import logging
import argparse
import psycopg2
import sys

# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)

logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect("dbname='snippet1' user='francis'")
logging.debug("Database connection established.")

def put(name, snippet):
    """Store a snippet with an associated name"""
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
    with connection, connection.cursor() as curs:
        try:
            command = "insert into snippets values (%s, %s)"
            curs.execute(command, (name, snippet))
        except psycopg2.IntegrityError as e:
            connection.rollback()
            command = "update snippets set message=%s where keyword=%s"
            curs.execute(command, (snippet, name))
    logging.debug("Snippet stored successfully.")
    return name, snippet
    
def get(name):
    """Retrieve the snippet with a given name.
    prints a warning message if keyword not available
    """
    logging.info("retrieving a snippet {!r}".format(name))
    with connection, connection.cursor() as curs:
        curs.execute("select message from snippets where keyword=%s", (name,))
        row = curs.fetchone()
    
    logging.debug("Snippet retrieved successfully.")
    
    # Print warning and exit if no snippet was found with that name.
    if not row:
        print("Keyword: {!r} not available".format(name))
        sys.exit()     
    return row[0]

def catalog():
    """Retrieve all avaliable keywords from snippet table"""
    logging.info("retrieving all snippets") 
    with connection, connection.cursor() as curs:
        command = "select keyword from snippets order by keyword"
        curs.execute(command)
        row = curs.fetchall()    
    return row
 
def search(string):
    """search for a string within the snippet messages and return snippets
    containing the string"""    
    logging.info("retrieving all snippets containing a given substring") 
    with connection, connection.cursor() as curs:
        command = "select keyword, message from snippets where message ilike "+"'%"+string+"%'"  
        curs.execute(command)
        row = curs.fetchall()    
    return row 

def main():
    """Main function"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="The name of the snippet")
    put_parser.add_argument("snippet", help="The snippet text")

    # Subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="The name of the snippet")
    
    # Subparser for the catalog function
    logging.debug("Constructing catalog subparser")
    catlog_parser = subparsers.add_parser("catalog", help="Available keywords")
    
    #Subparser for the search function
    logging.debug("Constructing search subparser")
    search_parser = subparsers.add_parser("search", help="Retrieve snippet containing a substring")
    search_parser.add_argument("string", help="The substring in the snippet")
        
    arguments = parser.parse_args(sys.argv[1:])
    
    # Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")
    
    if command == "put":
        name, snippet = put(**arguments)
        print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)        
        print("Retrieved snippet: {!r}".format(snippet))
    elif command == "catalog":        
        keys = []
        keywordlist = catalog(**arguments)  
        for values in keywordlist:
            keys.append(",".join(values))
        print("Available keywords: {!r}".format(keys)) 
    elif command == "search":
        for name, snippet in search(**arguments):
            print("Keyword:{!r}  Snippet:{!r}".format(name, snippet))

if __name__ == "__main__":
    main()
