import difflib
import re
import numpy as np
from astropy.table import Table
from astropy.table import join

from pagepy.abstracts import read_abstracts_table

### Step 0 - Check the abstract list ###
abstr = read_abstracts_table('../data/abstr0702.csv', autoacceptposters=False)
abstr['Email Address'] = [s.lower() for s in abstr['Email Address']]
ar, counts = np.unique(abstr['Email Address'], return_counts=True)
print('The following email addresses are associated with more than one abstract.')
print(ar[counts > 1])
print('')
ar, counts = np.unique(abstr['First author'], return_counts=True)
print('The following first authors submitted more than one abstract.')
print(ar[counts > 1])

### Step 1: Clean and check Jenine's file (i.e. remove canceled transactions etc.) ###
# - remove cancelled transactions
# - normalize name field in caps (some people use ALL CAPS NAMES)
# - remove title
jenine = Table.read('../data/jenine0620.csv', format='ascii')
# Remove rows at the end that don't have names in them
jenine = jenine[~jenine['Last Name'].mask]
# remove last row where headers are repeated
jenine = jenine[:-1]
for c in ['First Name', 'Last Name']:
    # The following is not correct for "van Dyck" etc, but good enough to match
    # and we won't use those names later on anyway.
    jenine[c] = [s.capitalize() for s in jenine[c]]
jenine['Email'] = [s.lower() for s in jenine['Email']]

jenine['name'] = ['{} {}'.format(jenine['First Name'][i], jenine['Last Name'][i]) for i in range(len(jenine))]

# Make the registration type column that Jenine deleted (or something similar)
# paid = [float(r.replace('$','').replace('-', '0')) for r in jenine['Dollar Amount PD']]
# jenine['Registration Type'] = table.MaskedColumn(data=paid, mask=np.array(paid) < 400)

### Step 2: Identify people with waivers in Jenine's list ###
## 2a) LOC members
LOC = Table.read('data/LOCmembers.csv', format='ascii')
LOC['name'] = [n.replace('(chair)', '').strip() for n in LOC['name']]
LOC['waiver'] = 'LOC'
LOC['mergeid'] = np.arange(len(LOC))
# OK, this gives us exact matches in name
tab = join(jenine, LOC, join_type='left')
# Now for those that are not matched yet
for mid in LOC['mergeid']:
    if not mid in tab['mergeid']:
        dname = difflib.get_close_matches(LOC['name'][mid], tab['name'], cutoff=0.8)
        # and here comes some hand sorting
        print(dname)
        if dname == ['Sarah Schmidt']:
            dname = []
        if len(dname) == 0:
            print('No match found for {}'.format(LOC['name'][mid]))
        else:
            ind = tab['name'] == dname[0]
            print('Matching {} to {}'.format(LOC['name'][mid], dname[0]))
            for c in ['waiver', 'mergeid']:
                tab[c][ind] = LOC[c][mid]

print('The following LOC members are not yet registered')
print(LOC['name'][np.isin(LOC['mergeid'], tab['mergeid'][~tab['mergeid'].mask], invert=True)])
tab.remove_column('mergeid')
## 2b) financial aid recipients
finaid = Table.read('../data/financialaid.csv', format='ascii')
finaid.keep_columns(['Email Address', 'Name'])
finaid['waiver'] = 'aid'
# table has all applicants, now restrict to people with approved aid
finaid = finaid[:74]
finaid.remove_row(-3)  # declined aid, so remove from list, too.

# OK, this gives us exact matches in name
tab.rename_column('Email', 'Email Address')
finaid['mergeid'] = np.arange(len(finaid))
tab2 = join(tab, finaid, join_type='left', keys=['Email Address'])
# Which email addresses are matched more than once?
mid, n = np.unique(tab2['mergeid'], return_counts=True)
mids = mid[(n > 1) & ~(mid.mask)]
print('Financial aid email addresses that turn up more than once in the registration list')
for n in mids:
    print (finaid[n])
print('-----')
tab2.rename_column('waiver_1', 'waiver')
tab2['waiver'][~tab2['waiver_2'].mask] = tab2['waiver_2'][~tab2['waiver_2'].mask]
tab2.remove_column('waiver_2')
# Now for those that are not matched yet use name
for mid in finaid['mergeid']:
    if not mid in tab2['mergeid']:
        dname = difflib.get_close_matches(finaid['Name'][mid], tab2['name'], cutoff=0.7)
        if len(dname) == 0:
            print('No match found for {}'.format(finaid['Name'][mid]))
        else:
            if len(dname) > 1:
                print("Name {} appears more than once. Assigning to first occurence.".format(dname))
            dname = [dname[0]]
            ind = tab2['name'] == dname[0]
            print('Matching {} to {}'.format(finaid['Name'][mid], dname[0]))
            for c in ['waiver', 'mergeid']:
                tab2[c][ind] = finaid[c][mid]

print('')
print('The following fin aid people are not yet registered')
print(finaid[np.isin(finaid['mergeid'], tab2['mergeid'][~tab2['mergeid'].mask], invert=True)])
tab2.remove_column('mergeid')

print('')
print('The following people are marked as WAIVER by Jenine, but do not have a waiver:')
ind_jan_waive = tab2['Comments'] == 'WAIVED'
print(tab2[ind_jan_waive & (tab2['waiver'] == '')]['Name', 'Email Address'])

### The following people with waivers paid for registration
print("The following people with waivers paid for registration and should be refunded")
tab2[~tab2['Registration Type'].mask & ~tab2['waiver'].mask]['Name', 'Email Address', 'waiver','Registration Type']

#### Now match to the abstracts
abstrshort = abstr[:]
#abstrshort.keep_columns(['Email Address', 'First author', 'Title', 'PaymentID'])
abstrshort.rename_column('PaymentID', 'Tran#')
abstrshort['LastName'] = [s.split()[-1] for s in abstrshort['First author']]

abstrshort['mergeid'] = np.arange(len(abstrshort))
confreg = ~tab2['Registration Type'].mask
for c in ['One Day Conference: Jul. 30th, 2018',
          'One Day Conference: Jul. 31st, 2018',
          'One Day Conference: Aug 1st, 2018',
          'One Day Conference: Aug 2nd, 2018',
          'One Day Conference: Aug 3rd, 2018',
          'waiver']:
    confreg = confreg | ~tab2[c].mask

confreg = confreg | (tab2['Comments'] == 'PYMNT PENDING')

confreg = tab2[confreg]
inddays = ~tab2['One Day Conference: Jul. 30th, 2018'].mask
for c in ['One Day Conference: Jul. 30th, 2018',
          'One Day Conference: Jul. 31st, 2018',
          'One Day Conference: Aug 1st, 2018',
          'One Day Conference: Aug 2nd, 2018',
          'One Day Conference: Aug 3rd, 2018']:
    inddays = inddays | ~tab2[c].mask

inddays = inddays
print("Number of registrations with financial aid: {}".format((confreg['waiver'] == 'aid').sum()))
print("Number of registrations from LOC: {}".format((confreg['waiver'] == 'LOC').sum()))

print("Number of total registrations (full, one day, or waved): {}".format(len(confreg)))
print("Number of people who registered for one or more days individually: {}".format(inddays.sum()))
print("Number of paid full registration (early + normal + late): {}".format((~tab2['Registration Type'].mask ).sum()))

tab2.rename_column('Title', 'Nametitle')

tab3 = join(tab2, abstrshort, join_type='left', keys=['Email Address'])
# Make to string because that's the format the abstract table has
tab3['Tran#'] = ['{}'.format(i) for i in tab3['Tran#_1']]

# Which email addresses are matched more than once?
mid, n = np.unique(tab3['mergeid'], return_counts=True)
mids = mid[(n > 1) & ~(mid.mask)]
print('Abstract email addresses that turn up more than once in the registration list')
for n in mids:
    print (abstrshort[n]['Email Address'])

print('-----')
print('Matching by Payment ID number given to me')
abstr_with_pymentid = abstrshort[abstrshort['Tran#'] != '']
abstrshort2 = abstrshort[abstrshort['Tran#'] == '']
if not (len(abstrshort2) + len(abstr_with_pymentid)) == len(abstrshort):
    raise ValueError('Tran# column is suspect')

tabtest1 = join(tab3, abstr_with_pymentid, join_type='outer', keys='Tran#')
tabtest2 = join(tab3, abstr_with_pymentid, join_type='left', keys='Tran#')
if len(tabtest1) != len(tabtest2):
    raise ValueError('Not all payment IDs exisit')

print(set(tabtest1['Tran#']) - set(tabtest2['Tran#']))

for mid in abstrshort['mergeid']:
    if not mid in tab3['mergeid']:
        if abstrshort['Tran#'][mid] != '':
            ind = tab3['Tran#'] == abstrshort['Tran#'][mid]
            for c in ['First author', 'Title', 'mergeid']:
                tab3[c][ind] = abstrshort[c][mid]

print('-----')
print('Matching by full name')
# Now for those that are not matched yet use Full Name
for mid in abstrshort['mergeid']:
    if not mid in tab3['mergeid']:
        dname = difflib.get_close_matches(abstrshort['First author'][mid], tab3['name'], cutoff=0.8)
        if len(dname) == 0:
            pass
            # print('No match found for {}'.format(abstrshort['First author'][mid]))
        else:
            if len(dname) > 1:
                print("Name {} appears more than once. Assigning to first occurence.".format(dname))
            dname = [dname[0]]
            ind = tab3['name'] == dname[0]
            print('Matching {} to {} using key {}'.format(abstrshort['First author'][mid], tab3['name'][ind].data, dname[0]))
            for c in ['First author', 'Title', 'mergeid']:
                tab3[c][ind] = abstrshort[c][mid]


# Then try last name
print('----')
print('Matching by last name and first name as far as known')
for mid in abstrshort['mergeid']:
    if not mid in tab3['mergeid']:
        dname = difflib.get_close_matches(abstrshort['LastName'][mid], tab3['Last Name'], cutoff=0.95)
        if len(dname) > 0:
            # initialize all False array
            ind = np.zeros(len(tab3), dtype=bool)
            for n in dname:
                ind = ind | (tab3['Last Name'] == n)
            # Now check that the first name matches as far as we know it (until the first "." or " ")
            abstrfirst = re.match('[\w]+', abstrshort['First author'][mid])
            for n in ind.nonzero()[0]:
                tabfirst = re.match('[\w]+', tab3['First Name'][n])
                minlen = min(abstrfirst.span()[1], tabfirst.span()[1])
                if abstrfirst.group()[:minlen] != tabfirst.group()[:minlen]:
                    ind[n] = False
            if ind.sum() == 1:
                print('Matching {} to {} using key {} {}'.format(abstrshort['First author'][mid], tab3['name'][ind].data, abstrfirst.group()[:minlen], dname[0]))
                for c in ['First author', 'Title', 'mergeid']:
                    tab3[c][ind] = abstrshort[c][mid]
            elif ind.sum() > 1:
                print('Multiple possible matches for {}: {} - match by hand'.format(abstrshort['First author'][mid], tab3['name'][ind].data))

print('The following abstr people are not yet registered')
abstrnoregistered = abstrshort[np.isin(abstrshort['mergeid'], tab3['mergeid'][~tab3['mergeid'].mask], invert=True)]
print(abstrnoregistered)
print('The following registered people did not submit an abstract:')
regnoabstr = tab3[tab3['mergeid'].mask]
print(tab3[tab3['mergeid'].mask]['name', 'Email Address'])
#tab3.remove_column('mergeid')

abstrnoregistered.sort('LastName')
regnoabstr.sort('Last Name')

abstrnoregistered['First author', 'LastName', 'Tran#'].show_in_browser(jsviewer=True)
regnoabstr['First Name', 'Last Name', 'Tran#'].show_in_browser(jsviewer=True)

print('Number of posters from registered participants: {}'.format((tab3['type'] == 'poster').sum()))

abstrregistered = abstrshort[np.isin(abstrshort['mergeid'], tab3['mergeid'][~tab3['mergeid'].mask])]

# Write out a table that allows me to find which authors are registered
abstrregistered[['Email Address']].write('../data/abstr0702_reg.csv', format='ascii.csv')



# Step X - read in full Jenine table
# Shift last few rows manually that were added
jfull = Table.read('../data/Coolstars20070318_shifted.csv', format='ascii')
# Check for double rows
# Cross match rows with each other
# Check numbers compared to the other spreadsheet I have