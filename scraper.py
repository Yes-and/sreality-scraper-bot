# import necessary libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import pandas as pd

import time
import math
import re
import random

class ScrapeBot():

    def __init__(self, url):
        self.url = url
        self.temp_df = pd.DataFrame()

    # Start the driver using correct args
    def startDriver(self, headless):

        # Used for debugging, running headless is preferred
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")

        # Location of the driver and settings
        self.driver = webdriver.Chrome("driver/chromedriver.exe", options = chrome_options)

        # Go to the url
        self.driver.get(self.url)

        # Make sure the driver is on
        self.active = True

    def endDriver(self):
        self.driver.quit()
        self.active = False

    # Approximate the num of remaining pages
    def getRemainPag(self):
        if self.active:

            # Get num of listings on page
            entries = self.driver.find_elements_by_class_name("numero")

            low_entries, high_entries = (entries[0].text.split("–"))
            low_entries = int(low_entries)
            high_entries = int(high_entries)

            total_entries = int(entries[1].text.replace(" ", ""))

            # Calculate the num of pages
            pages = (math.ceil( (total_entries-low_entries) / (high_entries-low_entries+1) ) )
            return pages

    # Select a specified part of page for scraping
    # Probably not needed, makes the code more bulletproof
    def getListings(self, curr_link):
        if self.active:
            # try:
            #     time.sleep(3)
            #     content = self.driver.find_element_by_class_name("dir-property_list")
            #     listings = content.find_elements_by_class_name("property")
            #     return listings
            # except:
            #     self.endDriver()
            #     self.url = curr_link
            #     self.startDriver(False)
            #     time.sleep(10)
            #     return self.getListings(curr_link)

            time.sleep(3)
            content = self.driver.find_element_by_class_name("dir-property-list")
            listings = content.find_elements_by_class_name("property")
            return listings

    # Locate nav bar and go to next pg
    def goNext(self):

        # Locate nav bar
        nav_bar = self.driver.find_elements_by_class_name("paging-full")[0]
        nav_entries = nav_bar.find_elements_by_class_name("paging-item")

        # Find the last button
        nav_next = nav_entries[len(nav_entries) - 1]
        nav_active = nav_next.find_element_by_tag_name("a")

        # Proceed to next pg
        nav_active.click()

    def openTab(self):
        self.driver.execute_script("window.open('');")
        window = self.driver.window_handles[1]
        self.driver.switch_to.window(window)
        time.sleep(1)

    def closeTab(self):
        self.driver.close()
        time.sleep(1)

    def getContents(self):

        title = self.driver.find_element_by_tag_name("h1")
        rooms = title.find_element_by_class_name("name").text
        location = title.find_element_by_class_name("location").text

        # Extract size
        try:
            size = re.findall("[0-9+kk]+", rooms)[0]
        except:
            size = None

        # Extract location
        try:
            part = re.findall("Praha [0-9]+", location)[0]
        except:
            part = None

        temp_dict = {}

        # Add extracted data to dictionary
        temp_dict["Nazev"] = rooms
        temp_dict["Pocet pokoju"] = size
        temp_dict["Lokace"] = location
        temp_dict["Mestska cast"] = part

        # Extract data from the table at the bottom and add to dictionary
        params = self.driver.find_element_by_class_name("params")
        entries = params.find_elements_by_tag_name("li")

        for entry in entries:

            # If the format is string
            temp_name = entry.find_element_by_tag_name("label").text
            temp_content = entry.find_element_by_tag_name("strong")

            # If the format is not string
            if len(temp_content.text) < 1:

                temp_bool = temp_content.find_elements_by_tag_name("span")[1]

                so = str(temp_bool.get_attribute("ng-if"))
                try:
                    re.findall("true", so)[0]
                    temp_content = True
                except:
                    temp_content = False

            # Important to get the text out of the element
            else:
                temp_content = temp_content.text

            # Add entry to dictionary
            temp_dict[temp_name] = temp_content

        return temp_dict


    def getLink(self, listing):
        if self.active:
            # Hyperlink element
            hyperlink = listing.find_element_by_class_name("title").get_attribute("href")

            return hyperlink

    def getID(self, link):

            # Posting ID
            extid = re.findall("/([0-9]+[0-9]$)", link)[0]
            return extid

    def scrape(self, startpg, startlis):
        if self.active:

            # Condition
            first_run = True

            current = startpg
            pages = self.getRemainPag()

            while current < pages:

                print("Current pg: " + str(current) + " out of " + str(pages))

                # Get listings currently on pg
                listings = self.getListings(self.driver.current_url)
                len_list = len(listings)

                if first_run:
                    start = startlis

                # The first listing is always skipped as it is a recommendation that changes after every reload
                else:
                    start = 1

                # Removing the precondition
                first_run = False

                for i in range(start, len_list-1):

                    print("current listing: " + str(i) + " out of " + str(len_list-1))

                    # Decrease the chance of detection
                    wait = random.uniform(0, 3)
                    time.sleep(wait)

                    temp_dict = {}

                    # Get the link for the curr listing
                    temp_link = self.getLink(listings[i])
                    temp_dict["Link"] = temp_link

                    # Get ID for the curr listing
                    temp_id = self.getID(temp_link)
                    temp_dict["ID"] = temp_id

                    # Open a new tab, load link and extract info and close tab
                    self.openTab()
                    self.driver.get(temp_link)
                    temp_dict.update(self.getContents())
                    self.closeTab()

                    # Add data to dataframe
                    self.temp_df = self.temp_df.append(temp_dict, ignore_index = True)

                # increment page selector
                temp_pages = self.getRemainPag()
                if temp_pages != pages:
                    pages = temp_pages
                current += 1

            self.endDriver()
            print("All done!")

    # Getter method
    def getData(self):
        return self.temp_df
