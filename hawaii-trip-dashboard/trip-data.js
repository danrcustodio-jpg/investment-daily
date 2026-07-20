/** Synced from hawaii-trip-overview.canvas.tsx — re-run extract_trip_from_canvas.py after edits */
window.HAWAII_TRIP = {
  meta: {
    title: 'Hawaii Trip Overview',
    subtitle: 'Oahu trip plan for Jul 21–28, 2026 (4 travelers).',
    travelerCount: 4,
  },
  schedule: [
    {
      dayLabel: 'Day 1',
      dateShort: 'Tuesday Jul 21',
      timelinePlan: 'Travel to Oahu + rental pickup',
      timeDetail:
        '8:05 AM DEN departure / 1:45 PM HNL arrival / 3:00 PM car pickup',
      refs:
        'SW BGQBJY · Avis 11639739US6 · dinner: Blue Water Shrimp (plan) or Royal Lobster Waikiki (optional)',
      notes:
        'Travel day, airport arrival, rental car pickup, hotel check-in, and easy dinner — default plan Blue Water Shrimp; [Royal Lobster Waikiki](https://www.theroyallobster.com/) is an optional swap or compare (see meal blocks).',
      details: [
        {
          kind: 'reservation',
          title: 'Southwest Airlines (outbound)',
          arriveBy:
            'Jul 21 — DEN terminal ~7:15 AM for 8:05 AM departure · scheduled land HNL ~1:45 PM',
          lines: [
            'Confirmation BGQBJY.',
            'DEN → OAK → HNL · Flights WN1240 (DEN–OAK) and WN2879 (OAK–HNL).',
            'Depart Denver (DEN) 8:05 AM · Arrive Honolulu (HNL) 1:45 PM · Total ~9h 40m (plane change Oakland).',
          ],
        },
        {
          kind: 'reservation',
          title: 'Lodging — The Grand Islander (Hilton Grand Vacations Club)',
          arriveBy: 'Jul 21 — front desk from 4:00 PM (check-in opens; keys after Avis)',
          lines: [
            'Reservation 724557005 · 2023 Kalia Rd, Honolulu, HI 96815 · (808) 983-7500.',
            'Check-in Tue Jul 21 from 4:00 PM · Check-out Fri Jul 24 10:00 AM · 2BR Premier Luxury Ocean View (per HGV confirmation).',
            'Present confirmation, photo ID, and valid credit card at check-in · Guest certificate lists Daniel Custodio — confirm full party of four with front desk.',
            'HGV Club: 1-800-932-4482 · input@hgvc.com',
          ],
        },
        {
          kind: 'transport',
          title: 'Avis rental car',
          arriveBy: 'Jul 21 — HNL Avis counter by 3:00 PM pickup',
          lines: [
            'Confirmation 11639739US6 · Toyota Camry or similar (automatic, unlimited mileage).',
            'Pickup 3:00 PM · Honolulu Intl Airport (HNL), 300 Rodgers Blvd, Honolulu, HI 96819 · (808) 210-0000.',
          ],
        },
        {
          kind: 'meal',
          title: 'Blue Water Shrimp & Seafood (planned dinner)',
          lines: [
            'Hilton Hawaiian Village · 2005 Kalia Rd, Honolulu, HI 96815 · Daily 9:00 AM–10:00 PM · (808) 955-5400 · No reservations.',
            'Website: bluewatershrimphi.com',
          ],
        },
        {
          kind: 'meal',
          title: 'Royal Lobster Waikiki (optional)',
          lines: [
            'Waikīkī · Optional instead of Blue Water Shrimp on Day 1, or bookmark for another evening.',
            'Menu, hours, and reservations: https://www.theroyallobster.com/',
          ],
        },
      ],
      dayParking: {
        venues: [
          {
            tripRef: 'Planned dinner · Hilton Hawaiian Village grounds',
            placeName: 'Blue Water Shrimp & Seafood (2005 Kalia Rd)',
            summaryLines: [
              'If you are already at Grand Islander / HHV with the car parked for the stay, you may only need to walk from your tower — ask the desk whether moving the car for dinner is necessary.',
              'HHV posts resort guest self-parking rates at garage entries (often pricey daily); nearby commercial garages sometimes undercut resort pricing — compare before you commit.',
            ],
            resourceLink: {
              label: 'Hilton Hawaiian Village — resort map / directions',
              href: 'https://www.hiltonhawaiianvillage.com/resort-information/',
            },
          },
          {
            tripRef: 'Optional dinner · Royal Lobster Waikiki',
            placeName: 'Royal Lobster Waikiki',
            summaryLines: [
              'If you dine here instead of Blue Water Shrimp, use typical central Waikīkī parking (mall garages, hotel validation) — confirm hours and any valet with the restaurant.',
            ],
            resourceLink: {
              label: 'Royal Lobster Waikiki',
              href: 'https://www.theroyallobster.com/',
            },
          },
        ],
      },
    },
    {
      dayLabel: 'Day 2',
      dateShort: 'Wednesday Jul 22',
      timelinePlan: 'Easy Waikiki day',
      timeDetail: 'Flexible',
      refs: 'Intl Market Place · hula option',
      notes:
        'Low-key Waikiki recovery day · Optional evening: free hula show at International Market Place (Wed qualifies — confirm time).',
      details: [
        {
          kind: 'activity',
          title: 'Waikiki / recovery day',
          lines: [
            'No bookings — beach, pool, light shopping, or sunset on the strip.',
          ],
        },
        {
          kind: 'location',
          title: 'Lodging',
          lines: [
            'The Grand Islander (HGVC) — Hilton Hawaiian Village resort complex · 2023 Kalia Rd.',
            'Surf shuttle Fri picks up at Ilikai Hotel valet (Ala Moana Blvd side) — short walk from Grand Islander towers.',
          ],
        },
        {
          kind: 'activity',
          title: 'International Market Place — entertainment',
          lines: [
            'Free “O Na Lani Sunset Stories” hula show — Simon lists Mon / Wed / Fri (sunset-style show — verify exact time & stage on mall Events for Jul 2026).',
            'Open-air shopping, Grand Lanai dining, family-friendly mall in central Waikiki · Typical center hours 10 AM–9 PM (confirm day-of).',
            'Info & map: https://www.simon.com/mall/international-market-place',
          ],
        },
      ],
      dayParking: {
        venues: [
          {
            tripRef: 'Optional evening · mall & Grand Lanai',
            placeName: 'International Market Place (Waikīkī)',
            summaryLines: [
              'Mall-operated garage (often listed near 2330 Kalākaua Ave); SP+ also associates with IMP at 2377 Kūhiō Ave — follow mall signage from Kalākaua / Kūhiō.',
              'Confirm current rates, hours, and height limits on the mall’s parking page before your visit.',
            ],
            resourceLink: {
              label: 'International Market Place — mall parking',
              href: 'https://shopinternationalmarketplace.com/visit-hours/mall-parking/',
            },
          },
          {
            tripRef: 'Ideas list · central Waikīkī dining',
            placeName: "Paia Fish Market Waikiki · Duke's Waikiki (examples)",
            summaryLines: [
              'Treat like other Waikīkī stops: nearby mall garages (e.g. International Market Place), Waikīkī Beach Walk, or hotel validation where you are already dining/shopping.',
              'Street parking is tight and metered; read signs carefully for residential-only zones.',
            ],
            resourceLink: {
              label: 'International Market Place — mall parking',
              href: 'https://shopinternationalmarketplace.com/visit-hours/mall-parking/',
            },
          },
        ],
      },
    },
    {
      dayLabel: 'Day 3',
      dateShort: 'Thursday Jul 23',
      timelinePlan: 'Turtle Canyon snorkel',
      timeDetail: '1:00 PM – 3:00 PM',
      refs: 'Booking 45620467',
      notes:
        'Midday Turtle Canyon snorkel tour (arrive 20–30 minutes early for check-in). Harbor-area parking options for this outing are in the Parking (snorkel day) block below.',
      details: [
        {
          kind: 'reservation',
          title: 'Hawaii Ocean Charters — Turtle Canyon Snorkel',
          arriveBy:
            'Jul 23 — Kewalo Basin Pier A by ~12:30 PM (20–30 min before 1:00 PM departure)',
          lines: [
            'Booking #45620467 · Small group “Big Kahuna” · 4 guests · Booked by Daniel Custodio.',
            'Tour window 1:00 PM – 3:00 PM · Sign waiver before boarding · 48-hour cancellation policy.',
          ],
        },
        {
          kind: 'activity',
          title: 'Snorkel tour',
          lines: [
            'Depart Kewalo Basin Harbor Pier A · Instruction en route · Turtle Canyon snorkel · Dolphins/whales possible seasonally.',
            'Bring swimsuit (on under clothes), reef-safe sunscreen applied before arrival (not on boat), towel, cash for crew gratuity.',
          ],
        },
        {
          kind: 'location',
          title: 'Meet / check-in',
          lines: [
            'Kewalo Basin Harbor Pier A · 1136 Ala Moana Blvd Pier A, Honolulu, HI 96814.',
            'Arrive 20–30 minutes early · Phone (808) 460-1516 · See Parking (snorkel day) in this day for maps and rates.',
          ],
        },
      ],
    },
    {
      dayLabel: 'Day 4',
      dateShort: 'Friday Jul 24',
      timelinePlan: 'Surf lesson + dinner',
      timeDetail: '8:25 AM pickup · 9:00–11:00 AM lesson · 5:30 PM dinner',
      refs: 'Ohana FQRYVW · #347993995 · Cajun Crab (Yelp)',
      notes:
        'Ohana Surf family surf (2 hr) with Ilikai pickup, then dinner at Cajun Crab Waikiki (Yelp reservation, party of 4).',
      details: [
        {
          kind: 'transport',
          title: 'Between Stay 1 & Stay 2 + surf timing',
          arriveBy:
            'Jul 24 — vacate Stay 1 by 10:00 AM checkout · Stay 2 keys from 4:00 PM',
          lines: [
            'Stay 1 ends Fri Jul 24 at 10:00 AM (confirm 724557005). Stay 2 begins same property Fri Jul 24 — check-in from 4:00 PM (confirm 724535505).',
            'Afternoon gap ~10 AM–4 PM: arrange bag storage / bell desk with Grand Islander so you are not dragging suitcases to surf or dinner.',
            'Surf shuttle returns to Ilikai ~11:40–11:55 AM — after Stay 1 checkout; showers/changing may need pool areas or lobby plan until Stay 2 keys.',
          ],
        },
        {
          kind: 'reservation',
          title: 'Ohana Surf Project — FareHarbor confirmation',
          lines: [
            'Order #FQRYVW · Booking #347993995 · Paid $646.12 · Booked by Jessica Custodio.',
            'Fri Jul 24, 2026 · 9:00 AM–11:00 AM · 4× Family Lesson (2 HR) · Surf Lessons!',
            '48-hour cancellation (phone to cancel or reschedule) · Sign online waiver/registration before the lesson.',
          ],
        },
        {
          kind: 'transport',
          title: 'Shuttle pickup (arrive 5 minutes early)',
          arriveBy: 'Jul 24 — Ilikai Hotel valet by ~8:20 AM (8:25 AM shuttle departure)',
          lines: [
            'Pick up at 8:25 AM · Ilikai Hotel — Ala Moana Blvd side of the hotel, valet front entrance (wait by valet and stairwell).',
            'Look for Surf School Bus vehicles · Late or missed pickup: call (808) 599-7873 immediately.',
            'Return: shuttle departs ~11:30 AM; typically back to your pickup area ~11:40–11:55 AM (one departure per lesson).',
          ],
        },
        {
          kind: 'activity',
          title: 'Lesson & after',
          lines: [
            'In-water lesson with transport to/from surf site (Queen’s Surf / “Publics” area).',
            'Reef-safe sunscreen required · Towel · Optional footage purchase (discount if prepaid — see FareHarbor email).',
            'Afterward: team shuttles to Ohana Surf Center to review lesson footage (per operator email).',
          ],
        },
        {
          kind: 'location',
          title: 'Alternate check-in (if not using Ilikai pickup)',
          lines: [
            'Ohana Surf Center at Waikiki Beach Marriott — 2552 Kalakaua Ave, Suite P159–P160 (use only if you switch to self-meet; your confirmation is Ilikai pickup).',
          ],
        },
        {
          kind: 'activity',
          title: 'Contact',
          lines: [
            '(808) 599-7873 · osp@ohanasurfproject.com · ohanasurfproject.com · FAQ: https://www.ohanasurfproject.com/FAQ/',
          ],
        },
        {
          kind: 'reservation',
          title: 'Cajun Crab Waikiki — Yelp Reservations',
          arriveBy: 'Jul 24 — restaurant by 5:30 PM reservation',
          lines: [
            'Fri Jul 24, 2026 · 5:30 PM · Party of 4.',
            'Manage or cancel in the Yelp app / links from your confirmation email.',
          ],
        },
        {
          kind: 'meal',
          title: 'Dinner',
          lines: ['Cajun Crab Waikiki.'],
        },
        {
          kind: 'location',
          title: 'Restaurant address',
          lines: [
            '226 Lewers St, 2F Unit L215, Honolulu, HI · (808) 913-2003.',
          ],
        },
      ],
      dayParking: {
        venues: [
          {
            tripRef: 'Dinner reservation · Waikīkī Beach Walk',
            placeName: 'Cajun Crab Waikiki (226 Lewers St)',
            summaryLines: [
              'Restaurant sits on Waikīkī Beach Walk — use that property’s garage / valet program rather than hunting for street-only stalls.',
              'Waikīkī Beach Walk publishes validation-style parking promotions (minimum purchase, participating merchants, time windows) — read the current rules on their Parking page before dinner.',
            ],
            resourceLink: {
              label: 'Waikīkī Beach Walk — Parking',
              href: 'https://www.waikikibeachwalk.com/Parking.htm',
            },
          },
        ],
      },
    },
    {
      dayLabel: 'Day 5',
      dateShort: 'Saturday Jul 25',
      timelinePlan: 'North Shore day (suggested)',
      timeDetail: 'Flexible',
      refs: 'Open day',
      notes:
        'Suggested: North Shore — Haleiwa, beaches, food trucks. Adjust when you firm up plans.',
      details: [
        {
          kind: 'activity',
          title: 'North Shore day trip (not booked)',
          lines: [
            'Typical loop: Haleiwa town, Waimea Bay, Sunset Beach, Banzai Pipeline viewpoints, food trucks / shave ice.',
            'Allow drive time from Waikiki (~1 hr each way depending on stops).',
            'More detail & parking strategy: Optional stops & ideas → Hawaii Fun sections (Waimea Valley/Beach, Haleiwa Town, beaches).',
          ],
        },
        {
          kind: 'location',
          title: 'Areas to map',
          lines: [
            'Haleiwa · Waimea Bay · Sunset Beach · Optional Laniakea Beach (turtles — safety/traffic caution).',
          ],
        },
      ],
    },
    {
      dayLabel: 'Day 6',
      dateShort: 'Sunday Jul 26',
      timelinePlan: 'Pearl Harbor — Arizona Memorial',
      timeDetail: '11:15 AM Arizona Memorial Tour · arrive Visitor Center 10:15 AM',
      refs: 'recreation.gov #0822792530-1 · 4 tickets',
      notes:
        'Booked: Arizona Memorial Tour at Pearl Harbor (recreation.gov) — 4 General Admission tickets, 11:15 AM boat, ticket holder Jessica Custodio. Afternoon is flexible (Diamond Head, east-side drive, Ala Moana Beach, or windward dinner at Haleiwa Joe’s Kaneohe).',
      details: [
        {
          kind: 'reservation',
          title: 'Arizona Memorial Tour — Pearl Harbor (recreation.gov)',
          arriveBy:
            'Jul 26 — Pearl Harbor Visitor Center by 10:15 AM (1 hr early) · Theater Validation Desk by 11:05 AM (10 min before 11:15 AM boat)',
          lines: [
            'Confirmation #0822792530-1 · 4 tickets · General Admission · Ticket holder: Jessica Custodio.',
            'Sun Jul 26, 2026 · 11:15 AM boat departure · Program length 45 minutes.',
            'Operator: Arizona Memorial Tours Pearl Harbor · Reservations non-transferable / non-refundable · Everyone in party (including children) must have a reservation.',
          ],
        },
        {
          kind: 'activity',
          title: 'Need to know — Arizona Memorial',
          lines: [
            'No bags, purses, or items offering concealment — privately operated bag storage near the visitor center for a fee. OK to bring: cameras, water bottles, wallets, cell phones.',
            'Only clear water allowed in the theater, on the boats, and at the USS Arizona Memorial — no other food or beverage.',
            'Site of major loss of life — practice cemetery etiquette: speak quietly, limit phone use, dress respectfully. Wheelchair accessible (wheelchairs not provided). No restrooms on the memorial itself; restrooms at the Visitor Center.',
            'More info: https://www.nps.gov/pearlharbor',
          ],
        },
        {
          kind: 'location',
          title: 'Pearl Harbor Visitor Center',
          lines: [
            '1 Arizona Memorial Place, Honolulu, HI 96818 · Parking $7/day via virtual pay system on mobile devices.',
            'About 25–30 min from Waikiki (no traffic) — leave Waikiki by ~9:30 AM to be safe for 10:15 AM Visitor Center arrival.',
          ],
        },
        {
          kind: 'activity',
          title: 'Afternoon — flexible',
          lines: [
            'After Pearl Harbor (~noon end): pair with another anchor or take a relaxed afternoon.',
            'Ideas: Diamond Head State Monument (entry reservation often required via gostateparks.hawaii.gov), east-side scenic drive / Kualoa, Ala Moana Beach Park, or windward dinner at Haleiwa Joe’s Kaneohe (Haiku Gardens) — see parking notes below.',
          ],
        },
      ],
      dayParking: {
        introNote:
          'Optional anchors from today’s ideas — use only what you actually book. Rates and hours change; confirm before you go.',
        venues: [
          {
            tripRef: 'Pearl Harbor Historic Sites',
            placeName: 'Pearl Harbor National Memorial (visitor center)',
            summaryLines: [
              'NPS operates paid visitor parking at the Pearl Harbor Visitor Center (fee posted on nps.gov — historically around single-digit dollars per day; pay via mobile app or kiosk as directed on site).',
              'Bag restrictions apply — review NPS “Plan Your Visit” before you arrive.',
            ],
            resourceLink: {
              label: 'NPS — Directions & transportation (Pearl Harbor)',
              href: 'https://www.nps.gov/valr/planyourvisit/directions.htm',
            },
          },
          {
            tripRef: 'Diamond Head summit hike',
            placeName: 'Diamond Head State Monument',
            summaryLines: [
              'State Parks requires advance online reservations for entry; parking is bundled with those reservations for drivers — no showing up without a booked window.',
              'Arrive within the first 30 minutes of your reservation slot or risk being turned away; exit by the end of your booked period.',
            ],
            resourceLink: {
              label: 'Diamond Head — reservations & fees (Go State Parks)',
              href: 'https://gostateparks.hawaii.gov/diamondhead/',
            },
          },
          {
            tripRef: 'Optional windward dinner · Haiku Gardens',
            placeName: "Haleiwa Joe's — Kaneohe (46-336 Haiku Rd)",
            summaryLines: [
              'Visitors commonly report a free on-site lot at Haiku Gardens; it can fill during peak dinner — plan to arrive earlier than reservation time if driving.',
            ],
            resourceLink: {
              label: "Haleiwa Joe's — locations",
              href: 'https://www.haleiwajoes.com/',
            },
          },
          {
            tripRef: 'Beach option · west of Waikīkī',
            placeName: 'Ala Moana Beach Park',
            summaryLines: [
              'Large public beach park — City & County manages lots with posted hours (typically daytime only; no overnight). Main access often from Ala Moana Park Drive near the lagoons.',
              'Confirm hours and any temporary closures on the official parks page before you go.',
            ],
            resourceLink: {
              label: 'Honolulu DPR — Ala Moana Regional Park',
              href: 'https://www.honolulu.gov/dpr/ala-moana-regional-park/',
            },
          },
        ],
      },
    },
    {
      dayLabel: 'Day 7',
      dateShort: 'Monday Jul 27',
      timelinePlan: 'Final full day + pack',
      timeDetail: 'Flexible',
      refs: 'Intl Market Place · hula option',
      notes:
        'Last full day on island · Optional evening: same free hula schedule includes Monday — pair with dinner at International Market Place if you like.',
      details: [
        {
          kind: 'activity',
          title: 'Final island day',
          lines: [
            'Revisit a favorite beach or shop for souvenirs · Confirm Tuesday airport timing (late flight).',
            'Pack bags; stage rental return documents and HNL departure checklist.',
          ],
        },
        {
          kind: 'activity',
          title: 'International Market Place — entertainment',
          lines: [
            'Free “O Na Lani Sunset Stories” hula show — Simon lists Mon / Wed / Fri (Jul 27 is a Monday — confirm time & location on Events page).',
            'Grand Lanai restaurants, shops, occasional live music at venues on property — check mall site for your date.',
            'https://www.simon.com/mall/international-market-place',
          ],
        },
      ],
      dayParking: {
        venues: [
          {
            tripRef: 'Optional evening · mall & Grand Lanai',
            placeName: 'International Market Place (Waikīkī)',
            summaryLines: [
              'Mall-operated garage (often listed near 2330 Kalākaua Ave); SP+ also associates with IMP at 2377 Kūhiō Ave — follow mall signage from Kalākaua / Kūhiō.',
              'Confirm current rates, hours, and height limits on the mall’s parking page before your visit.',
            ],
            resourceLink: {
              label: 'International Market Place — mall parking',
              href: 'https://shopinternationalmarketplace.com/visit-hours/mall-parking/',
            },
          },
          {
            tripRef: 'Ideas list · central Waikīkī dining',
            placeName: "Paia Fish Market Waikiki · Duke's Waikiki (examples)",
            summaryLines: [
              'Treat like other Waikīkī stops: nearby mall garages (e.g. International Market Place), Waikīkī Beach Walk, or hotel validation where you are already dining/shopping.',
              'Street parking is tight and metered; read signs carefully for residential-only zones.',
            ],
            resourceLink: {
              label: 'International Market Place — mall parking',
              href: 'https://shopinternationalmarketplace.com/visit-hours/mall-parking/',
            },
          },
        ],
      },
    },
    {
      dayLabel: 'Day 8',
      dateShort: 'Tuesday Jul 28',
      timelinePlan: 'Departure day + return flight',
      timeDetail: '7:00 PM car return / 8:50 PM HNL departure',
      refs: 'SW BGTK9Z',
      notes: 'Return car at 7:00 PM and depart Honolulu at 8:50 PM.',
      details: [
        {
          kind: 'transport',
          title: 'Grand Islander checkout (Stay 2)',
          arriveBy: 'Jul 28 — checkout / vacate by 10:00 AM',
          lines: [
            'Check-out Tue Jul 28 10:00 AM (HGV) · Flight 8:50 PM — use bag hold / late-day plan at resort after checkout until you head to Avis.',
          ],
        },
        {
          kind: 'transport',
          title: 'Avis return',
          arriveBy: 'Jul 28 — HNL Avis by 7:00 PM return',
          lines: [
            'Same location as pickup: HNL · 300 Rodgers Blvd, Honolulu, HI 96819 · Due by 7:00 PM · Confirmation 11639739US6.',
          ],
        },
        {
          kind: 'reservation',
          title: 'Southwest Airlines (return)',
          arriveBy:
            'Jul 28 — at HNL with time for check-in & security before 8:50 PM departure',
          lines: [
            'Confirmation BGTK9Z.',
            'HNL → LAX → DEN · Flights WN4082 (HNL–LAX) and WN1591 (LAX–DEN).',
            'Depart Honolulu 8:50 PM Tue Jul 28 · Arrive Denver 11:10 AM Wed Jul 29 (next calendar day) · Total ~10h 20m · Plane change LAX.',
          ],
        },
        {
          kind: 'location',
          title: 'Airport',
          lines: ['Daniel K. Inouye International Airport (HNL) · Allow time after car return for shuttle/walk to counters and security.'],
        },
      ],
    },
  ],
  flights: {
    outbound: {
      confirmation: 'BGQBJY',
      summaryLines: [
        'Denver (DEN) to Honolulu (HNL), Tue Jul 21.',
        'Departs 8:05 AM, arrives 1:45 PM with plane change in OAK.',
        'Confirmation BGQBJY.',
      ],
    },
    inbound: {
      confirmation: 'BGTK9Z',
      summaryLines: [
        'Honolulu (HNL) to Denver (DEN), Tue Jul 28 → Wed Jul 29.',
        'Departs 8:50 PM, arrives 11:10 AM next day with plane change in LAX.',
        'Confirmation BGTK9Z.',
      ],
    },
  },
  rental: {
    company: 'Avis',
    confirmation: '11639739US6',
    summaryLines: [
      'Pickup Tue Jul 21 at 3:00 PM, dropoff Tue Jul 28 at 7:00 PM at HNL.',
      'Reservation 11639739US6.',
    ],
  },
  activities: [
    {
      name: 'Turtle Canyon Snorkel',
      operator: 'Hawaii Ocean Charters',
      summaryLines: [
        'Thu Jul 23, 1:00 PM–3:00 PM.',
        'Booking 45620467.',
        'Meet at Kewalo Basin Harbor Pier A.',
      ],
    },
    {
      name: 'Surf Lessons (Family · 2 HR)',
      operator: 'Ohana Surf Project',
      summaryLines: [
        'Fri Jul 24, 2026 · 9:00 AM–11:00 AM · Order #FQRYVW · Booking #347993995.',
        'Shuttle pickup 8:25 AM · Ilikai Hotel, Ala Moana Blvd side — valet front entrance (Hilton Hawaiian Village / Ilikai).',
        '4 family lessons (Daniel, Jessica, Graham, Lillian) · Paid $646.12 · (808) 599-7873 · osp@ohanasurfproject.com.',
      ],
    },
    {
      name: 'Dinner — Cajun Crab Waikiki',
      operator: 'Yelp Reservations',
      summaryLines: [
        'Fri Jul 24, 2026 · 5:30 PM · Party of 4.',
        '226 Lewers St, 2F Unit L215, Honolulu, HI · (808) 913-2003.',
      ],
    },
    {
      name: 'Arizona Memorial Tour — Pearl Harbor',
      operator: 'Arizona Memorial Tours (recreation.gov)',
      summaryLines: [
        'Sun Jul 26, 2026 · 11:15 AM boat · 45-minute program · Ticket holder Jessica Custodio.',
        'Confirmation #0822792530-1 · 4 tickets · General Admission · Non-refundable / non-transferable.',
        'Arrive Visitor Center 10:15 AM (1 hr early) · Check in at theater Validation Desk by 11:05 AM · No bags allowed (paid bag storage nearby).',
      ],
    },
  ],
  parking: {
    longTerm: {
      title: 'Long-term parking (trip)',
      introNote:
        'Week- or month-length passes useful across multiple outings while you have the rental car. Amounts are estimates. Harbor campus overview:',
      resourceLink: {
        label: 'Kewalo Harbor',
        href: 'https://kewaloharbor.com/parking/',
      },
      options: [
        {
          priority: 'Maximum convenience',
          lotName: 'Ward Village — Aeʻo / Whole Foods garage',
          websiteUrl: 'https://www.wardvillage.com/information/',
          websiteLinkText: 'Ward Village (parking & info)',
          option: 'Garage weekly pass (buy on-site)',
          mapsAddress:
            '1001 Queen St, Honolulu, HI 96814 · Alt entrance: 388 Kamakee St, Honolulu, HI 96814.',
          estimatedCost: '~$200',
        },
        {
          priority: 'Lowest price',
          lotName: 'Kewalo Basin Harbor — OHA/HCDA lots (Diamond Parking monthly)',
          websiteUrl: 'https://www.diamondparking.com/',
          websiteLinkText: 'Diamond Parking',
          option: 'Harbor monthly permit',
          mapsAddress:
            '1125 Ala Moana Blvd B-1, Honolulu, HI 96814 — follow harbor signage to OHA/HCDA lots · (808) 592-7275.',
          estimatedCost: '$150',
        },
      ],
    },
    snorkelDayParking: {
      introNote:
        'Single-day choices for Pier A if you are not using a long-term pass from the section above. Researched reference — rates and hours change; confirm before you go.',
      venues: [
        {
          tripRef:
            'Thu Jul 23 · 1:00–3:00 PM · Booking #45620467 · Hawaii Ocean Charters',
          placeName: 'Turtle Canyon snorkel — meet Kewalo Basin Harbor Pier A',
          summaryLines: [
            'Tour window 1:00–3:00 PM · Arrive 20–30 minutes early for check-in (see day plan above for operator phone and waiver).',
          ],
        },
        {
          tripRef: 'Official harbor campus · layout & pay stations',
          placeName: 'Kewalo Basin Harbor — parking reference',
          summaryLines: [
            'Use the harbor site for campus parking overview before you go.',
          ],
          resourceLink: {
            label: 'Kewalo Harbor parking',
            href: 'https://kewaloharbor.com/parking/',
          },
        },
        {
          tripRef: 'Paste into navigation apps',
          placeName: 'Meet point & harbor lots (addresses)',
          summaryLines: [
            'Snorkel meet (Pier A): 1136 Ala Moana Blvd Pier A, Honolulu, HI 96814',
            'Harbor property / surface lots: 1125 Ala Moana Blvd B-1, Honolulu, HI 96814',
          ],
        },
        {
          tripRef:
            'Flexibility · Turtle Canyon · park on harbor campus — pay hourly for this visit',
          placeName: 'Kewalo Basin Harbor — pay stations (hourly)',
          summaryLines: [
            'Use this option: Harbor hourly (~$1/hr)',
            '1125 Ala Moana Blvd B-1, Honolulu, HI 96814 — pay stations on harbor property.',
            'Est. cost: Varies (~$110–$160 est. for trip patterns)',
          ],
          resourceLink: {
            label: 'Kewalo Harbor parking',
            href: 'https://kewaloharbor.com/parking/',
          },
        },
        {
          tripRef:
            'Walk-off convenience · Ward garage — walk to Pier A (daily pay if no weekly pass)',
          placeName: 'Ward Village — Aeʻo / Whole Foods garage',
          summaryLines: [
            'Use this option: Day garage / daily rate (buy on-site)',
            '1001 Queen St, Honolulu, HI 96814 · Alt entrance: 388 Kamakee St, Honolulu, HI 96814 · Short walk to Pier A.',
            'Est. cost: Daily rate (see garage)',
          ],
          resourceLink: {
            label: 'Ward Village (parking & info)',
            href: 'https://www.wardvillage.com/information/',
          },
        },
      ],
    },
  },
  optionalStops: {
    intro:
      'From your “Hawaii Fun” notes — verify hours, fees, surf conditions, and permits before you go.',
    food: {
      visits: [
        {
          title: 'Royal Lobster Waikiki',
          menuUrl: 'https://www.theroyallobster.com/',
          linkLabel: 'theroyallobster.com',
          summaryLines: [
            'Seafood / lobster-focused dining in Waikīkī — good optional swap for Day 1 arrival dinner or another night.',
            'Check the site for hours, reservations, and location before you go.',
          ],
        },
        {
          title: 'Waffle and Berry',
          menuUrl: 'https://waffleandberry.com/home',
          linkLabel: 'waffleandberry.com',
          summaryLines: [
            'Waikīkī Shopping Plaza — waffles, açaí bowls, desserts · 2250 Kalākaua Ave #LL104, Honolulu, HI 96815.',
            'Behind Victoria’s Secret corner side of the plaza; from plaza parking take elevator to level B, exit and turn right — details on site.',
          ],
        },
        {
          title: "Leonard's Bakery",
          menuUrl: 'https://leonardshawaii.com/home/',
          linkLabel: 'leonardshawaii.com',
          summaryLines: [
            'Malasadas, pāo doce, and bakes — 933 Kapahulu Ave, Honolulu (short drive from Waikīkī).',
            'Typical hours (confirm on site): daily ~5:30 AM–7:00 PM · (808) 737-5591.',
          ],
        },
        {
          title: 'Marugame Udon — Waikīkī',
          menuUrl: 'https://www.marugameudon.com/locations/waikiki/',
          linkLabel: 'Marugame Udon Waikiki',
          summaryLines: [
            'Udon · 2310 Kūhiō Ave Ste 124, Honolulu, HI 96815 · (808) 931-6000.',
            'Typical hours (confirm on site): daily ~10:00 AM–10:00 PM.',
          ],
        },
        {
          title: 'Musubi Cafe IYASUME',
          menuUrl: 'https://iyasumehawaii.com/',
          linkLabel: 'iyasumehawaii.com',
          summaryLines: [
            'Musubi, rice balls, bento — multiple Oʻahu stores; near Waikīkī: Beach Walk (227 Lewers St), Pacific Monarch (2427 Kūhiō Ave), Seaside (334 Seaside Ave) — see site for hours and phone by branch.',
            'Also Ala Moana, Keeaumoku, Kahala, and more — menu and locations on iyasumehawaii.com.',
          ],
        },
        {
          title: 'Monkeypod Kitchen',
          menuUrl: 'https://www.monkeypodkitchen.com/',
          linkLabel: 'monkeypodkitchen.com',
          summaryLines: [
            'Merriman group · casual-upscale Hawaiian regional — famous house-made mai tai, kiawe wood–fired plates, poke.',
            'On Oʻahu: Ko Olina (Kapolei / west resort strip) — good optional dinner if you spend a west-side afternoon; ~35–45+ min from Waikīkī depending on traffic (confirm address & hours on site).',
            'Other locations (Maui, etc.) listed on monkeypodkitchen.com if your plans change islands.',
          ],
        },
        {
          title: "Haleiwa Joe's — Kaneohe (Haiku Gardens)",
          menuUrl: 'https://www.haleiwajoes.com/kaneohe-menu',
          linkLabel: 'Kaneohe menu & info',
          summaryLines: [
            'Windward Oʻahu · Open-air dinner in Haiku Gardens — tropical grounds, koi pond, views of the Koʻolau range (per Haleiwa Joe’s).',
            'Dinner nightly 4:00–9:00 · (808) 247-6671 · 46-336 Haiku Rd, Kaneohe, HI 96744.',
            'Fits a flexible windward / east-side day (e.g. Day 6); not booked — call ahead if you want a table when busy.',
          ],
        },
      ],
      sections: [
        {
          heading: 'Waikīkī dining ideas',
          lines: [
            'Paia Fish Market Waikiki.',
            "Duke's Waikiki.",
            'Royal Lobster Waikiki — see Food stops above; also optional Day 1 meal in the day-by-day plan.',
            'Waffle and Berry — https://waffleandberry.com/home (Food stops above).',
            "Leonard's Bakery — https://leonardshawaii.com/home/ (malasadas · Kapahulu; Food stops above).",
            'Marugame Udon Waikīkī — https://www.marugameudon.com/locations/waikiki/ (Food stops above).',
            'Musubi Cafe IYASUME — https://iyasumehawaii.com/ (several locations; Food stops above).',
            'Monkeypod Kitchen — https://www.monkeypodkitchen.com/ (Ko Olina on Oʻahu + other islands; Food stops above).',
          ],
        },
        {
          heading: 'Shave ice — quick compare',
          table: {
            headers: ['Place', 'Best for…', 'Location'],
            rows: [
              [
                'Waiola Shave Ice',
                'Softest, fluffiest ice (the “local” pick)',
                'Kapahulu (near Waikīkī)',
              ],
              [
                'Island Vintage',
                'Real fruit syrups & gourmet toppings',
                'Royal Hawaiian Center',
              ],
              [
                "Ululani's",
                'Consistently high quality & award-winning',
                'Kapahulu Ave / Honolulu',
              ],
              [
                'Lahaina Shave Ice',
                'Convenience & beach views',
                'Waikīkī Shore (near Hilton)',
              ],
            ],
          },
        },
        {
          heading: 'Haleiwa Town — eats & treats',
          lines: [
            'Matsumoto Shave Ice — long-running shave ice spot.',
            'Haleiwa Fruit Shack — juices and drinks.',
            'Kono’s — slow-roasted pork / plate-lunch style (your notes).',
            'Farm to Barn — breakfast and drinks.',
            'Haleiwa Joe’s — scenic North Shore setting (chain also has Kaneohe — see Food stops above).',
          ],
        },
      ],
    },
    activities: {
      sections: [
        {
          heading: 'Waimea Valley & Waimea Beach (North Shore)',
          lines: [
            '~1 hr 4 min from hotel (your estimate) · Waimea Valley garden valley with trails; waterfall area has food service.',
            'Typical hours/fees (planning estimate): often ~9 AM–4 PM; closed some days · ~$25 adults / ~$14 children — confirm current.',
            'Swimming at waterfall: call (808) 633-7766 same day to confirm whether swimming is allowed.',
            'Strategy from notes: hit Waimea Beach ~9 AM for parking, then Waimea Falls · Cliff-jumping spot — use caution; winter currents · Good snorkeling too.',
            'Parking / access: main beach lot is tiny and fills fast · Alternatives: paid parking across from Waimea Valley (~$20 your notes) or nearby Catholic church (~$10 your notes) · On Kamehameha Hwy ~4.5 mi from Haleiwa.',
          ],
        },
        {
          heading: 'Hikes',
          lines: [
            'Lulumahu Falls — DLNR permit required (free permit + small processing fee) · ~100 permits/day · Reserve ahead via Hawaii DLNR “Lulumahu Falls Trail permit”.',
            'Trailhead parking: large unpaved lot near Nuʻuanu Pali Dr / Pali Hwy intersection · Treat lot as high petty-theft risk — nothing visible in car.',
            'Waimano Falls — on your list; confirm trail status and access separately.',
          ],
        },
        {
          heading: 'Ocean — snorkel & swim',
          lines: [
            'Sharks Cove — snorkeling; underwater cave swim on right side of cove (your notes) — match conditions and skill.',
            'Electric Beach — warm water attracts sea life including dolphins · Pavilion & restrooms · Your notes: theft risk at cars — hide valuables · Fins recommended for swim.',
          ],
        },
      ],
    },
    locations: {
      sections: [
        {
          heading: 'Beaches & bays ( Oʻahu )',
          lines: [
            'Ala Moana Beach — local beach ~10 min from hotel.',
            'Sunset Beach — sunsets; sand; Sunrise Shack nearby for açaí bowls (your notes).',
            'Laniakea (“turtle beach”) — south of Waimea Bay · Frequent turtles — stay ≥10 ft by law · Rocky shore · No restrooms · Turtles often morning.',
          ],
        },
        {
          heading: 'Haleiwa Town — stroll & shopping',
          lines: [
            '~53 min from hotel (your estimate) · Souvenir shopping · Food trucks or sit-down between stops — see Food → Haleiwa Town for specific spots.',
          ],
        },
      ],
    },
  },
  lodging: [
    {
      label: 'Stay 1 — confirmed',
      propertyName: 'The Grand Islander — Hilton Grand Vacations Club',
      summaryLines: [
        '2023 Kalia Rd, Honolulu, HI 96815 · (808) 983-7500 · Reservation 724557005.',
        'Tue Jul 21 → Fri Jul 24 · Check-in from 4:00 PM · Check-out 10:00 AM · 2BR Premier Luxury Ocean View.',
        'Guest certificate / confirmation names Daniel Custodio — verify all four travelers with front desk · Photo ID + credit card at check-in.',
        'Changes: 1-800-932-4482 · input@hgvc.com',
      ],
    },
    {
      label: 'Stay 2 — confirmed',
      propertyName: 'The Grand Islander — Hilton Grand Vacations Club',
      summaryLines: [
        'Same resort · 2023 Kalia Rd · (808) 983-7500 · Reservation 724535505.',
        'Fri Jul 24 → Tue Jul 28 · Check-in from 4:00 PM · Check-out 10:00 AM · 2BR Premier Ocean View (per confirmation).',
        'Back-to-back with Stay 1 (checkout Jul 24 10 AM) — same-day gap until 4 PM check-in; coordinate luggage with bell desk.',
        'Guest certificate Daniel Custodio · Changes: 1-800-932-4482 · input@hgvc.com',
      ],
    },
  ],
};
