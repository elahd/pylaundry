<div align="center">
<img src="https://user-images.githubusercontent.com/466460/174422077-452bdd5c-243b-4487-8bd8-07a0120284d2.png">
<h2>Python Interface for ESD / Hercules CyclePay Laundry Payment Systems</h2>
<p align="center">This is an unofficial project that is not affiliated with ESD or Hercules.</p>
</div>

## Purpose

pylaundry allows developers to make the ESD [CyclePay](https://esdcard.com/cyclepay/) system interoperable with custom scripts and third party systems like Home Assistant. The library supports querying machine status and virtual card balances. If your building's laundry room supports one of the below apps, you should be able to use pylibrary:

| Logo                                                                                                                           | Name              | Links                                                                                                                                                                    |
| ------------------------------------------------------------------------------------------------------------------------------ | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ![esd cyclepay logo](https://user-images.githubusercontent.com/466460/174422476-2e2804e7-7b4d-4d4e-b4b0-0b15b34d2d11.png)      | ESD CyclePay      | [[iOS]](https://apps.apple.com/us/app/cyclepay-laundry-app/id904361786) [[Android]](https://play.google.com/store/apps/details?id=com.esd.laundrylink&gl=US)             |
| ![hercules cyclepay logo](https://user-images.githubusercontent.com/466460/174422481-50703225-516d-40b6-abca-a9adc3e199a3.png) | Hercules CyclePay | [[iOS]](https://apps.apple.com/us/app/hercules-cyclepay/id1520002517?uo=4) [[Android]](https://play.google.com/store/apps/details?id=com.esd.laundrylink.hercules&gl=US) |

## Features

### Currently Available

1. Check card balance (CyclePay / virtual cards only).
2. Check whether washer/dryer is running and how much time is left in the current cycle, among other attributes.

### Roadmapped

1. Add time/money to a machine.
2. Add money to virtual card.

## Necessity

Between dorms and apartments, I've been using shared laundry rooms for around two decades. ESD makes, hands down, the worst laundry room equipment that I've ever used. I made this library to ease the frustration of being stuck with these systems. Here's a breakdown of how these systems are awful:

### ESD's Hardware Sucks

Funding a card-operated dryer in a normal laundry room is straightforward:

1. Insert card & wait for machine to read balance.
2. Press button for desired cycle. (Starts machine with ~30 minutes.)
3. To add more time, press the same cycle button. Each press adds ~5 minutes to the cycle.
4. Remove card when enough time has been added.

Then there's the steps for ESD's equipment:

1. Insert card & wait for machine to read balance.
2. Press button for desired cycle. (Starts machine with ~30 minutes.)
3. To add more time to the cycle, remove and re-insert the card, then wait for the machine to read the balance. Each dip add 5 minutes to the cycle.

Aside from being painfully slow, most re-dips result in a read error:

![ezgif com-gif-maker](https://user-images.githubusercontent.com/466460/174495294-14709554-cb30-4949-8f1a-650dc18784b9.gif)

To start a 60 minute dryer cycle, ESD customers need to dip their cards 6 times. This means that ESD chip cards and chip card readers wear out at 6x the speed of other equipment. This is purely anecdotal, but I've had to replace the laundry card in my current building 4 times in 3 years due to wear.

### ESD's Software Sucks

![ezgif com-gif-maker (1)](https://user-images.githubusercontent.com/466460/175664339-20e89114-fe58-4ae4-9261-4e5a8ea9b9c1.gif)
