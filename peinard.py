"""
PEINARD: chill out and let me do your balance and accounting.


This is just a small algorithm.


Copyright (C) 2010-2011
Created by Feth AREZKI <feth AT tuttu.info>
Contributions by Alexis Metaireau <alexis AT notmyidea org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


api:
    call heuristic(totals)

    where totals is a dict person -> credit.
    For instance: {<object1>: mkdec(5), <object2>: (-3), <object3>: mkdec(-2)}

    you'll get a collection of transfer instructions, like:
        giver, receiver, value

Requisite 1:
    Totals must be provided as decimal.Decimal.
    It's maybe easier if you use the util function 'mkdec'

Requisite 2:
    Totals must be balanced.

    Maybe evolution: drop this requisite and provide a NOBODY person,
    that will be used to balance the last debt/lend, leaving it up to the
    caller to assert there is no expected transfert to/from NOBODY, or that
    such a transfer is not exceeding a certain value.

How it works:
    While lends and debs, loop on the following:
        If exact matches are found, they are returned.
        Bigger values are then matched against each other such as to
        solve the 'problem' for one person at least.
"""

from itertools import product
from decimal import Decimal, getcontext


DEC_O = Decimal(0)
PRECISION = 6  # digits
CTX = getcontext()
CTX.prec = PRECISION


def exactmatch(lends, debts):
    """
    returns first exact match in lends/debts list

    (internal)
    """
    for lend, debt in product(lends, debts):
        if lend.is_exact_match(debt):
            return debt, lend

    # no match: return None


class Line(object):
    """
    Convenience internal object
    """
    def __init__(self, person, value):
        """
        Parameters
        ----------

        person: any object
        value: decimal.Decimal (made with mkdec for instance)
        """
        self.person = person
        self.value = value

    def __cmp__(self, other):
        """
        not the std comparison: uses absolute value
        """
        return int(self.value.compare_total_mag(other.value))

    def __lt__(self, other):
        """
        not the std comparison: uses absolute value
        """
        return self.value.copy_abs() < other.value.copy_abs()

    def transfer(self, other):
        """
        Perform biggest transfer possible between two Line.
        Returns value

        Assumes (and asserts) that self is the ower and other the lender.
        """
        assert self.value < 0
        value = self.value.min_mag(other.value).copy_abs()

        other.value = CTX.subtract(other.value, value)
        self.value = CTX.add(self.value, value)

        return value

    def is_exact_match(self, other):
        """
        Returns: do the lines oppose?
        """
        return self.value.compare_total_mag(other.value).is_zero()

    def __repr__(self):
        """
        >>> line = Line("a", 42)
        >>> print(line)  # doctest: +ELLIPSIS
        <peinard.Line object at 0x... person:a - value:42>
        """
        return object.__repr__(self).replace('>', ' person:%s - value:%s>' %
            (self.person, self.value))


def heuristic(totals):
    """
    Parameters
    ----------

    totals: a dict of object -> credit.
        credit is a Decimal
    """
    # structures
    debts = set()
    lends = set()
    result = set()

    for person, value in totals.items():
        if value.is_zero():
            result.add((person, None, DEC_O))
            continue

        line = Line(person, CTX.copy_decimal(value))

        if value > 0:
            lends.add(line)
            continue

        debts.add(line)

    assert all(lend.value > 0 for lend in lends), lends
    assert all(debt.value < 0 for debt in debts), debts

    #loop
    while lends or debts:
        #1st step: exact matches
        #iter on a copy of lends
        match = exactmatch(lends, debts)
        if match:
            debt, lend = match
            result.add((debt.person, lend.person, lend.value))
            lends.remove(lend)
            debts.remove(debt)
            continue  # loop the while

        #continue to 2nd step?
        if not lends and not debts:
            break
        assert bool(lends) == bool(debts), "Lends: %s, debts: %s" % (lends, debts)
        # find the biggest possible transfer
        # compute biggest transfer value
        biggestdebt = max(debts)
        biggestcredit = max(lends)
        # perform transfer
        transfer_value = biggestdebt.transfer(biggestcredit)
        assert transfer_value > 0  # otherwise it's wicked.
        # add to results
        result.add((biggestdebt.person, biggestcredit.person,
            transfer_value))
        # purge
        if biggestdebt.value.is_zero():
            debts.remove(biggestdebt)
        if biggestcredit.value.is_zero():
            lends.remove(biggestcredit)

    return result


def mkdec(value):
    """
    Util func: make decimals that look ok.
    Use in place of decimal.Decimal constructor

    Parameters
    ----------
    value: float, int (number)
    """
    return CTX.create_decimal(value)
