import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DraggableLinkComponent } from './draggable-link.component';

describe('DraggableLinkComponent', () => {
  let component: DraggableLinkComponent;
  let fixture: ComponentFixture<DraggableLinkComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DraggableLinkComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DraggableLinkComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
