import { ComponentFixture, TestBed } from '@angular/core/testing';

import { QuantumCircuitComponent } from './quantum-circuit.component';

describe('QuantumCircuitComponent', () => {
  let component: QuantumCircuitComponent;
  let fixture: ComponentFixture<QuantumCircuitComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ QuantumCircuitComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(QuantumCircuitComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
