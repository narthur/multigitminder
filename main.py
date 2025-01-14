import os
import time
import json
import ast
from datetime import datetime
from pyminder.pyminder import Pyminder


def process_sha():

    # Get SHA from environment
    sha = os.getenv('GITHUB_SHA')

    # If SHA is not provided set as empty string, else shorten sha to last 7 characters
    if (sha is None or len(sha) == 0):
        sha = ''
    else:
        sha = sha[:7]

    return sha


def process_ref():

    # Get REF
    ref = os.getenv('GITHUB_REF')

    # Shorten reference variable to branch name only
    ref = ref.split('/')[-1]

    return ref


def process_comment(comment, ref, sha):

    # If comment is not provided, use default
    if (comment is None or len(comment) == 0):
        print('Comment not provided. Using default comment.')
        comment = ref + '@' + sha + ' via multigitminder API call'

    return comment

def process_langs(target_langs, repo_langs):

    ## Check for valid repo_langs value
    if (repo_langs is None):
        raise ValueError('Repo languages is type None.')
    if not repo_langs:
        raise ValueError('Repo languages dictionary is empty.')
    
    # If target languages are provided
    if (len(target_langs) != 0):
        
        try:
            # Extract target_langs from array string
            target_langs = ast.literal_eval(target_langs)
        except Exception as e:
            # If only one target language provided, create new array
            target_langs = [ target_langs ]
        
        # Make each language in target_langs lowercase
        target_langs = [ lang.lower() for lang in target_langs ]

        # Parse repo_langs object
        repo_langs = json.loads(repo_langs)
        repo_langs = [ key.lower() for key,value in repo_langs.items() ] 

        # Matching languages
        matched_langs = [lang for lang in target_langs if lang in repo_langs]
        
        # If there is at least one target language in repo_langs proceed, else print error message and return
        if (len(matched_langs) > 0):
            langs_list = ''
            for i in matched_langs:
                langs_list += i + " "
            print('Target languages found: ' + langs_list + '\nLogging data to Beeminder.')
        else:
            raise ValueError('Target languages not found in repository language list.')
            

def main():

    # User variables
    username = os.getenv('INPUT_USERNAME')
    auth_token = os.getenv('INPUT_AUTH_TOKEN')
    goal_name = os.getenv('INPUT_GOAL')
    value = os.getenv('INPUT_VALUE')
    comment = os.getenv('INPUT_COMMENT')
    target_langs = os.getenv('INPUT_TARGET_LANGS')
    repo_langs = os.getenv('INPUT_REPO_LANGS')

    print(repo_langs)
    
    # Fail if username is not provided
    if (username is None or len(username) == 0):
        print('Error: Beeminder user name required')
        return

    # Fail if auth token is not provided.
    if (auth_token is None or len(auth_token) == 0):
        print('Error: Beeminder auth token not found')
        return

	# Fail if no goal provided.
    if (goal_name is None or len(goal_name) == 0):
        print('Error: Goal name not found.')
        return

	# Fail if no value provided.
    if (value is None or len(value) == 0):
        print('Error: Data value not found.')
        return

    # Process ref and sha
    ref = process_ref()
    sha = process_sha()

    # Process comment
    comment = process_comment(comment, ref, sha)

    # Process languages
    process_langs(target_langs, repo_langs)

    # Instantiate pyminder
    pyminder = Pyminder(user = username, token = auth_token)

    # Get goal
    goal = pyminder.get_goal(goal_name)
    
    # Stage datapoint for commit
    goal.stage_datapoint(value = value, comment = comment)
    
    # Commit datapoints to Beeminder API
    goal.commit_datapoints()

    # Output statement
    print(ref + '@' + sha + ': ' + 'Data point of ' + value + ' added to ' + goal_name + " with comment: '" + comment + "'")


if __name__ == "__main__":
    main()