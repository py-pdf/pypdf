// Package sample provides module docs.
package sample

import "fmt"

type PublicStruct struct {
	PublicField int
	privateField int
}

func PublicFunc() {}

func privateFunc() {}

type PublicInterface interface {
	PublicMethod()
}

func (s *PublicStruct) PublicMethod() {}

func (s *PublicStruct) privateMethod() {}
