import requests
import re
import json
from bs4 import BeautifulSoup
import time

# Nanoleaf configuration
UniversalIP = "192.168.0.182"
UniversalAuthCode = "IOe32CEizIqwNv15XNyk4ttlaT75jFE7"
defaultPort = "16021"

# Football team related vars
teamOneScore = 1
teamTwoScore = 1
inputUrl = False

# -*- coding: utf-8 -*-
"""
Validates that the URL is from sportinglife website and is valid
"""
def urlValidation():
    global inputUrl

    # If URL has not been entered-> Input email
    if not inputUrl:
        url = input("Please enter url of game to listen for: ")

        # If URL is not from website Sportinglife, make user try again
        if "sportinglife" not in url:
            print("URL must be provided from https://www.sportinglife.com")

            checkScore()
            return

        else:
            inputUrl = True
            return

# -*- coding: utf-8 -*-
"""
Checks score from sportinglife website via BS4
"""
def checkScore():
    global teamOneScore, url
    global teamTwoScore
    global inputUrl

    urlValidation()

    # If site is accepted -> Request Site HTML data
    response = requests.get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    type(html_soup)

    # Get Score & Teams from HTML
    score_containers = html_soup.find_all('span', class_='MatchScore__StyledScore-wxe8oz-2 dvrzWw')
    teamsPlaying = html_soup.find_all('h2', class_='TeamName__StyledTeamName-sc-1275yii-0 fagppE')

    # Try and assigned score to each var
    try:
        teamOne = score_containers[0].text
        teamTwo = score_containers[1].text

    # If error -> The game has probably not started
    except IndexError as error:
        print("This game has not started, try another team")
        inputUrl = False
        checkScore()
        return

    # If Team one has scored -> Get nanoleaf layout
    if int(teamOne) == teamOneScore:
        teamHasScored(teamsPlaying[0], "1")
        return

    # If Team two has scored -> Get nanoleaf layout
    elif int(teamTwo) == teamTwoScore:
        teamHasScored(teamsPlaying[1], "2")
        return

    # If no one has scored, re-run function
    else:
        time.sleep(1)
        checkScore()
        return

# -*- coding: utf-8 -*-
"""
Handles checking if a team has scored
Calls GetLayout when they have scored
"""
def teamHasScored(teamScored, teamNumber):
    checkScore.teamScored = teamScored.text

    if teamNumber == "1":
        teamOneScore += 1
    else:
        teamTwoScore += 1
    getLayout()


# -*- coding: utf-8 -*-
"""
Method is responsible for getting ID from the nanoleaves.
The Ids are fetched by iterating through a list of leaves from the network
A list of the leaf IDs is returned on the method call
"""
def getId(layout):
    leafId = []
    for i in range(len(layout)):
        if "panelId" in layout[i]:
            strippedData = layout[i].split(':')
            formatStripped = strippedData[1]
            temp = re.findall(r'\d+', formatStripped)
            leafId.append(temp)
    return leafId


# -*- coding: utf-8 -*-
"""
Method handles reading the teams RGB light data.
The method opens and reads a JSON file with all the teams in the premier league
"""


def readPixelsInFile():
    global jsonLeafColours
    leafId = getId(outputFormat)
    currentTeamColours = {}

    # For all leafs available
    for i in range(len(leafId)):
        x = 1

        # Assign var with name of team that scored
        teamName = checkScore.teamScored
        leafIdNum = str(leafId[i])
        leafIdNum.strip("[, ', ]")

        # Open JSON containing all team names
        path = "teams.json"
        with open(path, 'r') as j:
            teams = json.loads(j.read())

        # If team name is in JSON file
        if teamName in teams:
            # Create Array to temp store colours
            jsonLeafColours = []

            # While pointer is less than RGB values assigned to the teams (Always 3)
            while x <= 3:
                jsonLeafColours.append(str((teams[teamName][str(x)])))
                x = x + 1

            j.close()

        # Set Dictionary at first leaf ID index equal to the temp array created
        currentTeamColours[i] = jsonLeafColours

    return currentTeamColours


# -*- coding: utf-8 -*-
"""
This method is repsonsible for accessing the layout of the nanoleaves on the network
"""


def getLayout():
    global outputFormat

    # Send layout request to nanoleaves on network
    newResponse = requests.get("http://" + str(UniversalIP.rstrip()) + ":" + defaultPort + "/api/v1/" + str(UniversalAuthCode.rstrip()) + "/panelLayout/layout")
    output = str(newResponse.json())

    # Format output to be acceptable for packetBuilder
    outputFormat = output[output.index('['):]
    outputFormat = outputFormat.split('}')
    packetBuilder()
    return


# -*- coding: utf-8 -*-
"""
This method handles building the data to send to the leaves.
The leaf data is compiled into one efficient request and sent to the leaves once
"""


def packetBuilder():
    global numPanels
    leafId = getId(outputFormat)
    teamNanoleafColours = readPixelsInFile()

    f = open("PacketSent.txt", "w")
    animDataList = []

    # For the amount of leafs on the network
    for i in range(len(leafId)):
        numPanels = len(leafId)
        leafIdNum = str(leafId[i])
        currentLeafId = leafIdNum.strip("[, ', ]")

        # Display animation for 4 seconds
        timeDisplay = "4"

        animDataNew = currentLeafId + " " + str(len(teamNanoleafColours[i])) + " "
        animDataList.append(animDataNew)

        # For each RGB value in team values at current ID
        for x in range(len(teamNanoleafColours[i])):
            # Setup & Format time, number of panels and colours to send over network
            animTimeSetup = str(teamNanoleafColours[i][x].rstrip() + " 0 " + timeDisplay + " ")
            tempRGB = animTimeSetup.replace('\\n', '').replace("|", '').replace(",", '').replace("'", '').replace("[","").replace("]", "").replace("\"", "").replace("\\", "").replace("  ", " ")

            # Add current animation sequence to list
            animDataList.append(tempRGB)

    # Create 1 long string from list
    str1 = ''.join(animDataList)

    # Build custom animation command with packet data
    leafColour = ('{"write": {"animData": "' + '{0} {1}'.format(numPanels, str1[:-1]) + '","loop": true,"animType": "custom","palette": [],"version": "2.0","command": "display"}}')

    # Send long string to nanoleaves with request
    requests.put("http://" + str(UniversalIP.rstrip()) + ":" + defaultPort + "/api/v1/" + str(UniversalAuthCode.rstrip()) + "/effects", leafColour)

    # Write packet data to text document to spot syntax issues
    f.write(leafColour)

    checkScore()
    return

checkScore()
getLayout()
