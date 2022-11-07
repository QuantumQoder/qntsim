import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HowtouseComponent } from './howtouse.component';

describe('HowtouseComponent', () => {
  let component: HowtouseComponent;
  let fixture: ComponentFixture<HowtouseComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ HowtouseComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HowtouseComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
