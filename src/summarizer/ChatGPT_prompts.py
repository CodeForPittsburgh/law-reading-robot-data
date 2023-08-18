
def get_tagging_prompt(tags, text):
    return "Please examine the following text from the Pennsylvania State Legislature and provide up to 5 of the " \
           "following tags that you think best describe the text: \n\n" + text + "\n\n" + "Tags: " + ", ".join(tags) \
           + "\n\n" + "Text: "

def get_summary_prompt(text):
    return "Please provide a summary of the following text of a Bill from the Pennsylvania State Legislature: \n\n" + text

def get_revision_change_prompt(revision1, revision2):
    return "I am about to provide you with two versions of the same Bill from the Pennsylvania State Legislature. The " \
           "first is the preceding version, and the second is the new version. Please summarize how the text has " \
           "changed from the first to the second: \n\n Preceding Version:" + revision1 + "\n\n New Version: " + \
           revision2