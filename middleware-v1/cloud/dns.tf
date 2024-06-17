resource "aws_route53_record" "www-live" {
  zone_id = data.aws_route53_zone.public.zone_id
  name    = var.subject_alternative_names[0]
  type    = "CNAME"
  ttl     = 5

  weighted_routing_policy {
    weight = 100
  }

  set_identifier = "live"
  records        = [aws_alb.main.dns_name]
}

resource "aws_route53_record" "cache" {
  zone_id = data.aws_route53_zone.public.zone_id
  name    = var.cache_domain_name
  type    = "A"

  alias {
    name                   = module.cdn.cloudfront_distribution_domain_name
    zone_id                = module.cdn.cloudfront_distribution_hosted_zone_id
    evaluate_target_health = true
  }

}
