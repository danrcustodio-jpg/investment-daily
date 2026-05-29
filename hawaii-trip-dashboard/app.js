(function () {
  const trip = window.HAWAII_TRIP;
  const root = document.getElementById("root");

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  /** [label](url) → anchor */
  function formatInline(s) {
    const escaped = escapeHtml(s);
    return escaped.replace(
      /\[([^\]]+)\]\((https?:[^)]+)\)/g,
      '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
    );
  }

  function paragraphs(lines) {
    if (!lines || !lines.length) return "";
    return lines
      .map((line) => `<p>${formatInline(line)}</p>`)
      .join("");
  }

  function renderDetailBlock(b) {
    const arrive = b.arriveBy
      ? `<div class="arrive">Arrive by: ${formatInline(b.arriveBy)}</div>`
      : "";
    return `
      <div class="detail-card">
        <div class="kind">${escapeHtml(b.kind)}</div>
        <h4>${escapeHtml(b.title)}</h4>
        ${arrive}
        <div class="lines">${paragraphs(b.lines)}</div>
      </div>`;
  }

  function renderParkingVenues(venues) {
    if (!venues || !venues.length) return "";
    return venues
      .map(
        (v) => `
      <div class="parking-venue">
        <strong>${escapeHtml(v.placeName)}</strong>
        <div class="ref">${formatInline(v.tripRef)}</div>
        <div class="lines">${paragraphs(v.summaryLines)}</div>
        ${
          v.resourceLink
            ? `<a href="${escapeHtml(v.resourceLink.href)}" target="_blank" rel="noopener noreferrer">${escapeHtml(v.resourceLink.label)}</a>`
            : ""
        }
      </div>`
      )
      .join("");
  }

  function renderDayParking(dayParking, snorkel) {
    let html = "";
    if (dayParking && dayParking.introNote) {
      html += `<p class="note">${formatInline(dayParking.introNote)}</p>`;
    }
    if (dayParking && dayParking.venues && dayParking.venues.length) {
      html += renderParkingVenues(dayParking.venues);
    }
    if (snorkel) {
      html += `<div class="block-title">Snorkel day parking</div>`;
      if (snorkel.introNote) {
        html += `<p class="note">${formatInline(snorkel.introNote)}</p>`;
      }
      html += renderParkingVenues(snorkel.venues);
    }
    return html || "";
  }

  function renderOptionalSection(sec) {
    let h = "";
    if (sec.lines && sec.lines.length) {
      h += `<div class="lines">${paragraphs(sec.lines)}</div>`;
    }
    if (sec.table && sec.table.headers && sec.table.rows) {
      h += '<div class="table-scroll"><table><thead><tr>';
      sec.table.headers.forEach((cell) => {
        h += `<th>${escapeHtml(cell)}</th>`;
      });
      h += "</tr></thead><tbody>";
      sec.table.rows.forEach((row) => {
        h += "<tr>";
        row.forEach((cell) => {
          h += `<td>${formatInline(cell)}</td>`;
        });
        h += "</tr>";
      });
      h += "</tbody></table></div>";
    }
    return h;
  }

  if (!trip || !root) {
    if (root)
      root.innerHTML =
        '<p class="note">Could not load trip data. Ensure trip-data.js is present.</p>';
    return;
  }

  const stats = {
    days: `${trip.schedule.length} days`,
    travelers: String(trip.meta.travelerCount),
    activities: String(trip.activities.length),
    bookings: "3",
  };

  const timelineRows = trip.schedule.map((d) => [
    d.dateShort,
    d.timelinePlan,
    d.timeDetail,
    d.refs,
  ]);

  let timelineTable =
    '<div class="table-scroll"><table><thead><tr><th>Date</th><th>Plan</th><th>Time</th><th>Reference</th></tr></thead><tbody>';
  timelineRows.forEach((row) => {
    timelineTable += "<tr>";
    row.forEach((cell) => {
      timelineTable += `<td>${formatInline(cell)}</td>`;
    });
    timelineTable += "</tr>";
  });
  timelineTable += "</tbody></table></div>";

  let longTermRows = "";
  trip.parking.longTerm.options.forEach((o) => {
    longTermRows += `<tr>
      <td>${escapeHtml(o.priority)}</td>
      <td>${escapeHtml(o.lotName)}</td>
      <td><a href="${escapeHtml(o.websiteUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(o.websiteLinkText || "Website")}</a></td>
      <td>${escapeHtml(o.option)}</td>
      <td>${formatInline(o.mapsAddress)}</td>
      <td>${escapeHtml(o.estimatedCost)}</td>
    </tr>`;
  });

  let flightsHtml = "";
  flightsHtml += `<div class="block-title">Outbound</div>${paragraphs(trip.flights.outbound.summaryLines)}`;
  flightsHtml += `<div class="block-title">Return</div>${paragraphs(trip.flights.inbound.summaryLines)}`;
  flightsHtml += `<div class="block-title">Rental (${escapeHtml(trip.rental.company)})</div>${paragraphs(trip.rental.summaryLines)}`;
  flightsHtml += `<div class="block-title">Lodging</div>`;
  trip.lodging.forEach((stay) => {
    flightsHtml += `<div class="detail-card"><div class="kind">${escapeHtml(stay.label)}</div><h4>${escapeHtml(stay.propertyName)}</h4><div class="lines">${paragraphs(stay.summaryLines)}</div></div>`;
  });

  let activitiesHtml = "";
  trip.activities.forEach((a) => {
    activitiesHtml += `<div class="detail-card"><h4>${escapeHtml(a.name)} (${escapeHtml(a.operator)})</h4><div class="lines">${paragraphs(a.summaryLines)}</div></div>`;
  });

  let optionalFoodHtml = `<p class="note">${formatInline(trip.optionalStops.intro)}</p>`;
  optionalFoodHtml += `<div class="block-title">Bookmarked spots</div>`;
  trip.optionalStops.food.visits.forEach((v) => {
    optionalFoodHtml += `<div class="detail-card">
      <div class="visit-title">${escapeHtml(v.title)}</div>
      ${
        v.menuUrl
          ? `<a class="visit-link" href="${escapeHtml(v.menuUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(v.linkLabel || "Website")}</a>`
          : ""
      }
      <div class="lines">${paragraphs(v.summaryLines)}</div>
    </div>`;
  });
  trip.optionalStops.food.sections.forEach((sec) => {
    optionalFoodHtml += `<div class="sec-heading">${escapeHtml(sec.heading)}</div>`;
    optionalFoodHtml += renderOptionalSection(sec);
  });

  let optionalActHtml = "";
  trip.optionalStops.activities.sections.forEach((sec) => {
    optionalActHtml += `<div class="sec-heading">${escapeHtml(sec.heading)}</div>`;
    optionalActHtml += renderOptionalSection(sec);
  });

  let optionalLocHtml = "";
  trip.optionalStops.locations.sections.forEach((sec) => {
    optionalLocHtml += `<div class="sec-heading">${escapeHtml(sec.heading)}</div>`;
    optionalLocHtml += renderOptionalSection(sec);
  });

  let daysHtml = "";
  trip.schedule.forEach((day) => {
    const showSnorkel = day.dayLabel === "Day 3";
    const parkingBlock = renderDayParking(
      day.dayParking,
      showSnorkel ? trip.parking.snorkelDayParking : null
    );
    const details = (day.details || []).map(renderDetailBlock).join("");
    daysHtml += `
      <details class="panel">
        <summary>${escapeHtml(day.dayLabel)} — ${escapeHtml(day.dateShort)}</summary>
        <div class="body">
          <p class="note">${formatInline(day.notes)}</p>
          ${details}
          ${
            parkingBlock
              ? `<hr class="sep"/><div class="block-title">Parking</div>${parkingBlock}`
              : ""
          }
        </div>
      </details>`;
  });

  root.innerHTML = `
    <header class="banner">
      <h1>${escapeHtml(trip.meta.title)}</h1>
      <p class="sub">${escapeHtml(trip.meta.subtitle)}</p>
    </header>

    <div class="stats">
      <div class="stat"><label>Trip length</label><span>${escapeHtml(stats.days)}</span></div>
      <div class="stat"><label>Travelers</label><span>${escapeHtml(stats.travelers)}</span></div>
      <div class="stat"><label>Booked activities</label><span>${escapeHtml(stats.activities)}</span></div>
      <div class="stat"><label>Travel bookings</label><span>${escapeHtml(stats.bookings)}</span></div>
    </div>

    <details class="panel" open>
      <summary>Timeline snapshot</summary>
      <div class="body">${timelineTable}</div>
    </details>

    <details class="panel">
      <summary>Flights, car &amp; lodging</summary>
      <div class="body">${flightsHtml}</div>
    </details>

    <details class="panel">
      <summary>Booked activities</summary>
      <div class="body">${activitiesHtml}</div>
    </details>

    <details class="panel">
      <summary>Parking — long-term (trip)</summary>
      <div class="body">
        <p class="note">${formatInline(trip.parking.longTerm.introNote)}
          <a href="${escapeHtml(trip.parking.longTerm.resourceLink.href)}" target="_blank" rel="noopener noreferrer">${escapeHtml(trip.parking.longTerm.resourceLink.label)}</a>.
        </p>
        <div class="table-scroll"><table>
          <thead><tr>
            <th>Priority</th><th>Lot</th><th>Web</th><th>Option</th><th>Address</th><th>Est.</th>
          </tr></thead>
          <tbody>${longTermRows}</tbody>
        </table></div>
      </div>
    </details>

    <details class="panel">
      <summary>Optional — Food</summary>
      <div class="body">${optionalFoodHtml}</div>
    </details>

    <details class="panel">
      <summary>Optional — Activities</summary>
      <div class="body">${optionalActHtml}</div>
    </details>

    <details class="panel">
      <summary>Optional — Locations</summary>
      <div class="body">${optionalLocHtml}</div>
    </details>

    <section aria-label="Day by day">
      <div class="block-title" style="margin:18px 0 10px;font-size:0.85rem;">Day-by-day</div>
      ${daysHtml}
    </section>
  `;
})();
