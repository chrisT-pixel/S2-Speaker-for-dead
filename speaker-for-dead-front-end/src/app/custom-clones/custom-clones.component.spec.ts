import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CustomClonesComponent } from './custom-clones.component';

describe('CustomClonesComponent', () => {
  let component: CustomClonesComponent;
  let fixture: ComponentFixture<CustomClonesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CustomClonesComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CustomClonesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
