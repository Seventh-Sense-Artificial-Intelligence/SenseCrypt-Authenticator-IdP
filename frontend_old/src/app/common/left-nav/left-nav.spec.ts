import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LeftNav } from './left-nav';

describe('LeftNav', () => {
  let component: LeftNav;
  let fixture: ComponentFixture<LeftNav>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LeftNav],
    }).compileComponents();

    fixture = TestBed.createComponent(LeftNav);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
