import pandas

pd = pandas.read_excel('/Users/ctheissen/Google Drive/CS22_Planning_Documents/Registration/Reports/Registrant Details_Full_6.6.xlsx')

print(pd)

total = len(pd)
print(total)

# above_35 = titanic[titanic["Age"] > 35]

totalin  = len(pd[pd["Registration Type"]=="Conference Attendee"])
totalvir = len(pd[pd["Registration Type"]=="Conference Attendee - Virtual"])
print(totalin)

print("<p>%s participants are currently registered (%s in-person, %s remotely):</p>"%(total, totalin, totalvir))
print()
print('<ul class="listing">')
print()
lastname = ''
for i in range(len(pd)):

    #print(pd['Full Name'][i], pd['Company Name'][i], pd['Amount Due'][i], pd['Amount Paid'][i], pd['Amount Ordered'][i])
    #print(pd['Amount Paid'][i] == 0) 
    #print((pd['Amount Ordered'][i] > 1000 and pd['Amount Due'][i] > 800))
    #print((pd['Amount Ordered'][i] < 800 and pd['Amount Due'][i] >= 540))
    #print((pd['Amount Paid'][i] == 0 and pd['Amount Due'][i] != 0))
    #print((pd['Amount Paid'][i] == 0 and pd['Amount Due'][i] != 0) or (pd['Amount Ordered'][i] > 1000 and pd['Amount Due'][i] > 800))
    #print((pd['Amount Ordered'][i] < 800 and pd['Amount Due'][i] >= 540))
    #if (pd['Amount Due'][i] != 0) or (pd['Amount Ordered'][i] > 1000 and pd['Amount Due'][i] > 800): continue
    if (pd['Amount Paid'][i] == 0 and pd['Amount Due'][i] != 0) or (pd['Amount Ordered'][i] > 1000 and pd['Amount Due'][i] > 800): continue
    if (pd['Amount Ordered'][i] < 800 and pd['Amount Due'][i] >= 540): continue
    name        = pd['Full Name'][i]
    #print(name)
    institution = pd['Company Name'][i]
    if pd['Registration Type'][i] == "Conference Attendee - Virtual": type1 = "virtual"
    elif pd['Registration Type'][i] == "Conference Attendee": type1 = "in-person"
    if name == lastname:
        print('SAME NAME')
        break
    lastname = name

    print('<li><span style="color: #00629B;"> %s </span> - %s [%s]</li>'%(name, institution, type1))
    print()
    #break