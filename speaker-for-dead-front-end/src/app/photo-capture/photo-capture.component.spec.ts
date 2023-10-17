import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PhotoCaptureComponent } from './photo-capture.component';

describe('PhotoCaptureComponent', () => {
  let component: PhotoCaptureComponent;
  let fixture: ComponentFixture<PhotoCaptureComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PhotoCaptureComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PhotoCaptureComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
