//! Crate module doc.

use std::io;

pub struct PublicStruct {
    pub field: i32,
    private_field: i32,
}

pub fn public_fn() {}

fn private_fn() {}

pub trait PublicTrait {
    fn method(&self);
}

impl PublicStruct {
    pub fn method(&self) {}
    fn private_method(&self) {}
}
