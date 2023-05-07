import csv
import feedparser

# Dictionary listing the name of the csv file and the URL of the RSS feed
feeds = {
    'HouseBillsAndResolutions': 'https://www.legis.state.pa.us/WU01/LI/RSS/HouseBills.xml',
    'SenateBillsAndResolutions': 'https://www.legis.state.pa.us/WU01/LI/RSS/SenateBills.xml',
    'HouseSessionCalendar': 'https://www.legis.state.pa.us/WU01/LI/RSS/CAL/HouseCalendarSS0reg.xml',
    'SenateSessionCalendar': 'https://www.legis.state.pa.us/WU01/LI/RSS/CAL/SenateCalendarSS0reg.xml',
    'HouseDailySessionReports': 'https://www.legis.state.pa.us/WU01/LI/RSS/DailySessionReports.xml',
    'SenateSessionNotes': 'https://www.legis.state.pa.us/WU01/LI/RSS/SenateNotes.xml',
    'HouseCommitteeMeetingSchedule': 'https://www.legis.state.pa.us/WU01/LI/RSS/CMSH.xml',
    'SenateCommitteeMeetingSchedule': 'https://www.legis.state.pa.us/WU01/LI/RSS/CMSS.xml',
    'HouseLegislativeJournals': 'https://www.legis.state.pa.us/WU01/LI/RSS/HouseJournals.xml',
    'SenateLegislativeJournals': 'https://www.legis.state.pa.us/WU01/LI/RSS/SenateJournals.xml',
    'HouseRollCallVotes': 'https://www.legis.state.pa.us/WU01/LI/RSS/HRC.xml',
    'SenateRollCallVotes': 'https://www.legis.state.pa.us/WU01/LI/RSS/SRC.xml',
    'HouseVotedAmendments': 'https://www.legis.state.pa.us/WU01/LI/RSS/FA/HouseAmendments.xml',
    'SenateFloorAmendments': 'https://www.legis.state.pa.us/WU01/LI/RSS/FA/SenateAmendments.xml',
    'HouseCoSponsorshipMemoranda': 'https://www.legis.state.pa.us/WU01/LI/RSS/HouseCosponsorship.xml',
    'SenateCoSponsorshipMemoranda': 'https://www.legis.state.pa.us/WU01/LI/RSS/SenateCosponsorship.xml',
    'HouseMembers': 'https://www.legis.state.pa.us/WU01/LI/RSS/HouseMembers.xml',
    'SenateMembers': 'https://www.legis.state.pa.us/WU01/LI/RSS/SenateMembers.xml',
    'HouseCommitteeAssignments': 'https://www.legis.state.pa.us/WU01/LI/RSS/HouseCommitteeAssignments.xml',
    'SenateCommitteeAssignments': 'https://www.legis.state.pa.us/WU01/LI/RSS/SenateCommitteeAssignments.xml',
    'SenateExecutiveNominationsCalendar': 'https://www.legis.state.pa.us/WU01/LI/RSS/NominationsCalendar.xml',
}

for name, url in feeds.items():
    # Parse the RSS feed
    feed = feedparser.parse(url)

    # If the feed has no entries, skip it
    if len(feed.entries) == 0:
        continue

    # Get the child keys from the first item in the feed
    # We assume that all items in the feed have the same child keys
    keys = list(feed.entries[0].keys())

    # Open a new CSV file for writing
    with open('rss_data/' + name + '.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write the header row
        writer.writerow(keys)

        # Write the data rows
        for entry in feed.entries:
            row = [entry.get(key, '') for key in keys]
            writer.writerow(row)

