import doorman as d

def main():
    driver = d.Doorman()
    print("driver created!")

    intentOne = "Who is at the door"
    response, _ = driver.handleRequest(intentOne)
    print(response)

    intentTwo = "when was the person at the door last here"
    response, _ = driver.handleRequest(intentTwo)
    print(response)

    intentThree = "how do I know this person"
    response, _ = driver.handleRequest(intentThree)
    print(response)


    intentFour = "who does this person know here"
    response, _ = driver.handleRequest(intentFour)
    print(response)

    intentFive = "when was their birthday"
    response, _ = driver.handleRequest(intentFive)
    print(response)

    intentSix = "why were they here"
    response, _ = driver.handleRequest(intentSix)
    print(response)


    intentSeven = "update the date of last visit"
    response, _ = driver.handleRequest(intentSeven)
    print(response)

    intentEight = "how many times have they been here"
    response, _ = driver.handleRequest(intentEight)
    print(response)
if __name__ == "__main__":
    main()
