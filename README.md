<p align="center"><img src="https://user-images.githubusercontent.com/466460/174422077-452bdd5c-243b-4487-8bd8-07a0120284d2.png"></p>
<h1 align="center">Python Interface for ESD / Hercules CyclePay Laundry Payment Systems</h2>
<p align="center">This is an unofficial project that is not affiliated with ESD or Hercules.</p>
<br />
<p align="center">
  <a href="https://www.codacy.com/gh/elahd/pylaundry/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=elahd/pylaundry&amp;utm_campaign=Badge_Grade"><img src="https://app.codacy.com/project/badge/Grade/73d1f839d824412591ae91fbd9416de7"/></a>
  <a href="https://www.codacy.com/gh/elahd/pylaundry/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=elahd/pylaundry&amp;utm_campaign=Badge_Coverage"><img src="https://app.codacy.com/project/badge/Coverage/73d1f839d824412591ae91fbd9416de7"/></a>
  <a href="https://results.pre-commit.ci/latest/github/elahd/pylaundry/main"><img src="https://results.pre-commit.ci/badge/github/elahd/pylaundry/main.svg" /></a>
  <a href="https://pypi.org/project/pylaundry/"><img alt="PyPI" src="https://img.shields.io/pypi/v/pylaundry"></a>
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" /></a>
  <a href="https://github.com/PyCQA/pylint"><img src="https://img.shields.io/badge/linting-pylint-yellowgreen" /></a>
  <a href="https://github.com/elahd/pylaundry/blob/main/LICENSE"><img alt="GitHub" src="https://img.shields.io/github/license/elahd/pylaundry"></a>
</p>

## Purpose

pylaundry allows developers to make the ESD CyclePay system interoperable with custom scripts and third party systems like Home Assistant. The library supports querying machine status, checking virtual card balances, and using your virtual card to add money to machines. If your building's laundry room supports one of the below apps, you should be able to use pylaundry:

| Logo                                                                                                                           | Name              | Links                                                                                                                                                                    |
| ------------------------------------------------------------------------------------------------------------------------------ | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ![esd cyclepay logo](https://user-images.githubusercontent.com/466460/174422476-2e2804e7-7b4d-4d4e-b4b0-0b15b34d2d11.png)      | ESD CyclePay      | [[iOS]](https://apps.apple.com/us/app/cyclepay-laundry-app/id904361786) [[Android]](https://play.google.com/store/apps/details?id=com.esd.laundrylink&gl=US)             |
| ![hercules cyclepay logo](https://user-images.githubusercontent.com/466460/174422481-50703225-516d-40b6-abca-a9adc3e199a3.png) | Hercules CyclePay | [[iOS]](https://apps.apple.com/us/app/hercules-cyclepay/id1520002517?uo=4) [[Android]](https://play.google.com/store/apps/details?id=com.esd.laundrylink.hercules&gl=US) |

## Home Assistant <img src="https://user-images.githubusercontent.com/466460/179556124-ceaa5ade-ee45-4d00-8a7c-5f3436818775.png" width="20px" />

This library powers the [CyclePay for Home Assistant](https://github.com/elahd/ha-cyclepay) custom integration.

## Warnings

1. **Pylaundry can spend your money.** Theoretically, a bug in this code could drain your entire laundry card or otherwise spend more than you intended.
2. **Pylaundry is not endorsed or supported by ESD, Hercules, or their business partners.** Use of this library may have negative consequences, including but not limited to being banned from CyclePay.

**Use pylaundry _at your own risk_.**

## Features

### Currently Available

1. Check card balance (CyclePay / virtual cards only).
2. Add money to machine from virtual laundry card.
3. Check whether washer/dryer is running and how much time is left in the current cycle, among other attributes.

## Airing of Grievances

<img src="https://user-images.githubusercontent.com/466460/178060626-e447b18d-51ce-4cab-b366-a15063b17048.png" width="300px" />

I wrote this library after moving into a building with ESD hardware. Doing laundry is my zen activity. Adding money to a dryer with ESD's hardware is not zen. Here's why:

### Hardware

<img src="https://user-images.githubusercontent.com/466460/174495294-14709554-cb30-4949-8f1a-650dc18784b9.gif" width="200px" />

Well designed commercial dryers let users add time to their cycle by pressing the dryer's start button. One press adds 30 minutes to the timer and starts the cycle; every additional press adds 5 minutes. **ESD revisited this solved problem and delievered a card reader that requires users to _remove and redip_ their card once for each vend.** One dip (and press) adds 30 minutes to the timer; every additional dip adds 5 minutes. This is what loading a 60 minute dryer cycle looks like:

1. Insert card; wait for machine to read the card's balance.
2. Press button for desired cycle. This adds 30 minutes to the timer and starts the machine.
3. Remove and reinsert card; wait for machine to read the card's balance. +5 minutes; now 35 minutes on timer.
4. Re-dip; wait for the machine to read the card's balance. Except it can't read the balance and displays a card read error instead. Timer is still at 35 minutes.
5. Re-dip; wait; +5 min; now 40 min on timer.
6. Re-dip; wait; +5 min; now 45 min on timer.
7. Re-dip; wait; read error. Still at 45.
8. Re-dip; wait; read error. Still at 45.
9. Re-dip; wait; read error. Still at 45.
10. Re-dip; wait; +5 min; now 50 min on timer.
11. Re-dip; wait; +5 min; now 55 min on timer.
12. Re-dip; wait; read error. Still at 55.
13. Re-dip; wait; +5 min; now 60 min on timer.

Now you're done!

Just kidding. You have a family, so you get to repeat that process a few more times for your remaining loads.

Additionally, all other things being equal, these extra dips mean that **ESD chip cards and chip card readers probably wear out six times earlier than competitor hardware** as ESD cards need to be dipped 6 times more per cycle. This is anecdotal, but I've had to replace the laundry card in my current building 4 times in 3 years due to wear.

### Software

About a year into living in my current apartment, ESD rolled out support for their CyclePay app. "Finally," I thought, "I can reclaim my zen activity." Nope. CyclePay is just as frustrating.

I expected CyclePay to just let me add, say, 60 minutes to a dryer with one or two taps. New medium, new medium-appropriate workflow.

In actuality, the app just mimics the workflow of the physical chip cards by forcing users to virtually swipe virtual cards. One swipe adds the first 30 minutes; each additional swipe adds another 5 minutes. Each swipe requires 4 taps and takes around 6 seconds — if you're fast — requires tapping through _two_ separate confirmations, and requires that you re-select your machine after every swipe. So...

---
**Loading 3 dryers with 60 minutes each takes 84 — _EIGHTY FOUR !!!!!_ — taps.**

**That's _insane_.**

**In a perfect environment, those 84 taps take a brain melting _2 minutes and 6 seconds_ to complete.**

...and that's if you're standing right in front of the machine (allowing CyclePay to vend via Bluetooth). If you want to finish loading your dryers while going back to your apartment, the app vends using the laundry machines' Wi-Fi connections. The app takes ~5 times as long to vend over Wi-Fi and relies on the machines being connected to WiFi in the first place, which they are often not. In my laundry room, around 10% of the machines seem to be disconnected at any time.

---

![ezgif com-gif-maker (3)](https://user-images.githubusercontent.com/466460/175664816-ade25bef-5671-4ae3-bc25-afcff224a38c.gif)
