import { AfterViewInit, Component, OnInit } from '@angular/core';
import { ConditionsService } from 'src/services/conditions.service';
import Globe from 'globe.gl';
import * as D3 from 'd3';
import * as _ from 'underscore';
import { any } from 'underscore';
@Component({
  selector: 'app-home-page',
  templateUrl: './home-page.component.html',
  styleUrls: ['./home-page.component.less']
})
export class HomePageComponent implements OnInit, AfterViewInit {
  constructor(private conService: ConditionsService) { }
  ngOnInit(): void {
    this.conService.currentSection = 'home'
  }
  ngAfterViewInit(): void {
    var globe = <HTMLElement>document.getElementById('globe');
    console.log("col-5" + globe.clientHeight)
    const parallax = document.getElementById("parallax")!;
    // Parallax Effect for DIV 1
    window.addEventListener("scroll", function () {
      let offset = window.pageYOffset;
      parallax.style.backgroundPositionY = offset * 0.4 + "px";
      // DIV 1 background will move slower than other elements on scroll.
    })
    const COUNTRY = 'India';
    const OPACITY = 0.5;
    const myGlobe = Globe()
      (<HTMLElement>document.getElementById('globeViz'))
      .globeImageUrl('//unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
      .pointOfView({
        lat: 28.7041,
        lng: 77.1025,
        altitude: 2
      }) // aim at continental US centroid
      .height(globe.clientHeight / 1.5)
      .width(globe.clientWidth)
      .backgroundColor('#000')
      .arcLabel((d: any) => `${d.airline}: ${d.srcIata} &#8594; ${d.dstIata}`)
      .arcStartLat((d: any) => +d.srcAirport.lat)
      .arcStartLng((d: any) => +d.srcAirport.lng)
      .arcEndLat((d: any) => +d.dstAirport.lat)
      .arcEndLng((d: any) => +d.dstAirport.lng)
      .arcDashLength(0.25)
      .arcDashGap(1)
      .arcDashInitialGap(() => Math.random())
      .arcDashAnimateTime(4000)
      .arcColor((d: any) => [`rgba(255, 255,255, ${OPACITY})`, `rgba(255, 0, 0, ${OPACITY})`])
      .arcsTransitionDuration(0)
      .pointColor(() => 'orange')
      .pointAltitude(0)
      .pointRadius(0.02)
      .pointsMerge(true);
    // myGlobe.position.y = 1000;
    // load data
    const airportParse = ([airportId, name, city, country, iata, icao, lat, lng, alt, timezone, dst, tz, type, source]: any) => ({
      airportId,
      name,
      city,
      country,
      iata,
      icao,
      lat,
      lng,
      alt,
      timezone,
      dst,
      tz,
      type,
      source
    });
    const routeParse = ([airline, airlineId, srcIata, srcAirportId, dstIata, dstAirportId, codeshare, stops, equipment]: any) => ({
      airline,
      airlineId,
      srcIata,
      srcAirportId,
      dstIata,
      dstAirportId,
      codeshare,
      stops,
      equipment
    });
    Promise.all([
      fetch('https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat').then(res => res.text())
        .then(d => D3.csvParseRows(d, airportParse)),
      fetch('https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat').then(res => res.text())
        .then(d => D3.csvParseRows(d, routeParse))
    ]).then(([airports, routes]) => {
      const byIata = _.indexBy(airports, 'iata', false);
      const filteredRoutes = routes
        .filter((d: any) => byIata.hasOwnProperty(d.srcIata) && byIata.hasOwnProperty(d.dstIata)) // exclude unknown airports
        .filter((d: any) => d.stops === '0') // non-stop flights only
        .map((d: any) => Object.assign(d, {
          srcAirport: byIata[d.srcIata],
          dstAirport: byIata[d.dstIata]
        }))
        .filter((d: any) => d.srcAirport.country === COUNTRY && d.dstAirport.country !== COUNTRY); // international routes from country
      myGlobe.controls().autoRotate = true;
      // myGlobe.position.y = -1000
      myGlobe
        .pointsData(airports)
        .arcsData(filteredRoutes);
    });
  }
}
