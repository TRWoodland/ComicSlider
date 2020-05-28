XmlDict = {'Title':'Night Shift', 'Series':'Marvel Zombies 4', 'Number':'2', 'Count':'4', 'Volume':'2009', 'AlternateSeries':'Dark Reign', 'Notes':'Scraped metadata from ComicVine [CVDB156658].', 'Year':'2009', 'Month':'7', 'Writer':'Fred Van Lente', 'Penciller':'Kevin Walker', 'Inker':'Kevin Walker', 'Colorist':'Jean-Francois Beaulieu', 'Letterer':'Rus Wooton', 'CoverArtist':'Greg Land, Justin Ponsor', 'Editor':'Bill Rosemann, Joe Quesada, Michael Horwitz, Ralph Macchio', 'Publisher':'Marvel', 'Web':'http://www.comicvine.com/', 'PageCount':'24'}

import email

def test_mp_form():
    msg = email.message_from_binary_file("test.bin")
    print(type(msg))
    if email.is_multipart():
        for part in email.get_payload():
            print(part.get_payload())
    else:
        print(email.get_payload(decode=True))


