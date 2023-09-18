import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OptimizationResultsComponent } from './optimization-results.component';

describe('OptimizationResultsComponent', () => {
  let component: OptimizationResultsComponent;
  let fixture: ComponentFixture<OptimizationResultsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ OptimizationResultsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OptimizationResultsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
