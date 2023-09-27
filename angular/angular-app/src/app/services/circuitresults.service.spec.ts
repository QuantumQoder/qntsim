import { TestBed } from '@angular/core/testing';

import { CircuitResultsService } from './circuitresults.service';

describe('CircuitResultsService', () => {
  let service: CircuitResultsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CircuitResultsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
