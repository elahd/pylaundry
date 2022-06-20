<div align="center">
<img src="https://user-images.githubusercontent.com/466460/174422077-452bdd5c-243b-4487-8bd8-07a0120284d2.png">
<h2>Python Interface for ESD / Hercules CyclePay Laundry Payment Systems</h2>
<p align="center">This is an unofficial project that is not affiliated with ESD or Hercules.</p>
<p align="center"><a href="https://badge.fury.io/py/pylaundry"><img src="https://badge.fury.io/py/pylaundry.svg" alt="PyPI version" height="18"></a></p>
</div>

# Purpose

pylaundry allows developers to make the ESD CyclePay system interoperable with custom scripts and third party systems like Home Assistant. The library supports querying machine status and virtual card balances. If your building's laundry room supports one of the below apps, you should be able to use pylibrary:

| Logo                                                                                                                           | Name              | Links                                                                                                                                                                    |
| ------------------------------------------------------------------------------------------------------------------------------ | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ![esd cyclepay logo](https://user-images.githubusercontent.com/466460/174422476-2e2804e7-7b4d-4d4e-b4b0-0b15b34d2d11.png)      | ESD CyclePay      | [[iOS]](https://apps.apple.com/us/app/cyclepay-laundry-app/id904361786) [[Android]](https://play.google.com/store/apps/details?id=com.esd.laundrylink&gl=US)             |
| ![hercules cyclepay logo](https://user-images.githubusercontent.com/466460/174422481-50703225-516d-40b6-abca-a9adc3e199a3.png) | Hercules CyclePay | [[iOS]](https://apps.apple.com/us/app/hercules-cyclepay/id1520002517?uo=4) [[Android]](https://play.google.com/store/apps/details?id=com.esd.laundrylink.hercules&gl=US) |

# Features

## Currently Available

1. Check card balance (CyclePay / virtual cards only).
2. Check whether washer/dryer is running and how much time is left in the current cycle, among other attributes.

## Roadmapped

1. Add time/money to a machine.
2. Add money to virtual card.
