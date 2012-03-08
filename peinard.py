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
    For instance: {<object1>: 5, <object2>: -3, <object3>: -2}

    you'll get a collection of transfer instructions, like:
        giver, receiver, value

Requisite:
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

from decimal import Decimal, getcontext


DEC_O = Decimal(0)
PRECISION = 6  # digits


def _exactmmatch(personstotals, total):
    """
    personstotals is expected as a list of (person, credit)
    The sign of credit is opposite to the sign of total and person
    is not contained in personstotals
    """
    for otherperson, othertotal in personstotals:
        if othertotal.compare_total_mag(total).is_zero():
            return otherperson


def _reverseabsvalue(item, otheritem):
    """
    Parameters
    ----------
    item: tuple with a Decimal as 2nd item
    otheritem: tuple with a Decimal as 2nd item
    """
    return int(item[1].copy_abs().compare(otheritem[1].copy_abs()))


def heuristic(totals):
    """
    Parameters
    ----------

    totals: a dict of object -> credit.
        credit is a Decimal
    """
    #initialization
    # decimal context
    context = getcontext()
    context.prec = PRECISION
    # structures
    debts = [
        [person, value]
        for person, value in totals.iteritems()
        if value < DEC_O
    ]
    lends = [
        [person, value]
        for person, value in totals.iteritems()
        if value > DEC_O
    ]
    result = [
        (person, None, DEC_O)
        for person, value in totals.iteritems()
        if value == DEC_O
    ]
    #loop
    while lends or debts:
        #1st step: exact matches
        #iter on a copy of lends
        for person, value in tuple(lends):
            match = _exactmmatch(debts, value)
            if match:
                result.append((match, person, value))
                lends.remove(
                    [person, value]
                )
                debts.remove(
                    [match, - value]
                )
        #continue to 2nd step?
        if not lends and not debts:
            break
        if bool(lends) != bool(debts):
            assert False, "Lends: %s, debts: %s" % (lends, debts)
        #prepare 2nd step
        debts.sort(_reverseabsvalue)
        lends.sort(_reverseabsvalue)
        #2nd step: make the biggest possible transfer
        biggestdebt = debts[0][1]
        biggestcredit = lends[0][1]
        #min_mag: minimum of absolute values
        transfer = biggestdebt.min_mag(biggestcredit)
        result.append((debts[0][0], lends[0][0], transfer))
        debts[0][1] = context.add(biggestdebt, transfer)
        lends[0][1] = context.subtract(biggestcredit, transfer, )
        #purge
        for collection in (lends, debts):
            for item in tuple(collection):
                if item[1].is_zero():
                    collection.remove(item)

    return result
